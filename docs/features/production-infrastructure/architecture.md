# Architecture: Production Cloud Infrastructure

## 1. System Overview & Deployment Topology
The production infrastructure for RIGHT FIT is designed according to **Option B: EC2 Container Workload Host + Amazon RDS PostgreSQL 16 Multi-AZ + Private Redis + Private S3 Object Storage**.

```mermaid
flowchart TD
    Internet["Public Internet / Candidates"] -->|"HTTPS:443 / HTTP:80"| NGINX["Edge Reverse Proxy (Nginx)"]

    subgraph VPC["AWS Dedicated VPC (10.0.0.0/16)"]
        subgraph Tier1["Tier 1: Public Subnets (10.0.1.0/24, 10.0.2.0/24)"]
            NGINX
            NAT["NAT Gateway (Outbound Egress)"]
        end

        subgraph Tier2["Tier 2: Private Application Subnets (10.0.10.0/24, 10.0.11.0/24)"]
            subgraph EC2["EC2 Workload Host (t4g.xlarge / ARM64)"]
                FRONTEND["Next.js 16 Web App (:3000)"]
                BACKEND["FastAPI Core Engine (:8000)"]
                WORKER["Celery Background Worker"]
                LEADHUNTER["LeadHunter Satellite (:8001)"]
                STARTUPS["Startup Intel Satellite (:8002)"]
                REDIS["Private Redis 7 (:6379)"]
            end
        end

        subgraph Tier3["Tier 3: Isolated Database Subnets (10.0.20.0/24, 10.0.21.0/24)"]
            RDS_PRIMARY["Amazon RDS PostgreSQL 16 (Primary)"]
            RDS_STANDBY["Amazon RDS PostgreSQL 16 (Standby)"]
        end
    end

    subgraph AWS_SERVICES["AWS Managed Services"]
        S3_RESUMES["S3 Private Resumes Bucket"]
        S3_BACKUPS["S3 Private Backups Bucket"]
        SSM["AWS SSM Parameter Store"]
        CW["CloudWatch Logs & Metrics"]
    end

    NGINX -->|"proxy_pass"| FRONTEND
    NGINX -->|"proxy_pass /api/"| BACKEND
    BACKEND -->|"asyncpg (Port 5432)"| RDS_PRIMARY
    BACKEND -->|"redis://:6379"| REDIS
    WORKER -->|"redis://:6379"| REDIS
    WORKER -->|"SQLAlchemy"| RDS_PRIMARY
    BACKEND -.->|"internal HTTP"| LEADHUNTER
    BACKEND -.->|"internal HTTP"| STARTUPS
    BACKEND -->|"presigned URLs"| S3_RESUMES
    RDS_PRIMARY -.->|"Sync Replication"| RDS_STANDBY
    EC2 -->|"Outbound HTTPS"| NAT
    EC2 -.->|"IAM Role (No Keys)"| SSM
    EC2 -.->|"IAM Role"| S3_RESUMES
    EC2 -.->|"IAM Role"| S3_BACKUPS
    EC2 -.->|"Metrics & Logs"| CW
```

## 2. Structural Layer Boundaries
1. **Tier 1 (Public Subnets)**:
   - Contains edge Nginx reverse proxy listening on ports 80 and 443.
   - Contains NAT Gateway routing outbound requests (e.g. Gemini AI API calls, ATS scrapers) from private workloads to the internet.
   - No application databases or internal services reside here.
2. **Tier 2 (Private Application Subnets)**:
   - Houses the container compute instances.
   - All services execute within isolated Docker networks:
     - `rightfit-ingress-net`: Connected only to Nginx and Frontend.
     - `rightfit-internal-net`: Internal bridge for Backend, Worker, Redis, and satellite adapters.
   - Instances lack public IP addresses and can only be accessed via AWS Systems Manager.
3. **Tier 3 (Isolated Database Subnets)**:
   - Houses Amazon RDS PostgreSQL 16 Multi-AZ.
   - Subnets have **zero route table entries to the Internet Gateway or NAT Gateway**.
   - Database ingress is strictly filtered by security group to allow connections only from `sg_app` on port 5432.

