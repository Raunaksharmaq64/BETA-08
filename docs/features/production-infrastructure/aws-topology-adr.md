# AWS Topology Architecture Decision Record

## 1. Summary of Architecture Options Evaluated

### Option A: Single EC2 with Docker Compose
- **Architecture**: A single virtual machine (`t4g.2xlarge`) hosting all containers (Nginx, Next.js, FastAPI, Celery, PostgreSQL, and Redis) on EBS volumes.
- **Cost**: \$70 – \$95 / month.
- **Trade-off**: Lowest cost, but single point of failure (SPOF). High disaster risk: database corruption or host failure requires manual EBS snapshot restore, yielding unacceptable RTO/RPO for candidate data.

### Option B: EC2 Container Workload Host + Managed RDS Multi-AZ + Private Redis (SELECTED)
- **Architecture**: Application containers run on a dedicated EC2 instance (`t4g.xlarge`) orchestrating workloads via non-root Docker Compose. Relational database is offloaded to Amazon RDS PostgreSQL 16 Multi-AZ with automated continuous backups, 30-day point-in-time recovery, and KMS storage encryption. Private Redis runs on internal network with AOF persistence.
- **Cost**: \$180 – \$260 / month.
- **Trade-off**: Balanced operational complexity, 99.95% database availability, strict network isolation, and seamless upgrade path to ECS.

### Option C: Container-Oriented AWS Architecture (ECS/Fargate + ALB + Multi-AZ RDS + ElastiCache)
- **Architecture**: Serverless container orchestration across AWS Fargate, Application Load Balancer, Amazon Aurora/RDS PostgreSQL, and multi-node Amazon ElastiCache Redis cluster.
- **Cost**: \$450 – \$750 / month.
- **Trade-off**: Highest horizontal scalability and zero server management, but incurs substantial baseline idle costs before reaching high user concurrency.

## 2. Decision Matrix
See full justification in [`ADR-0003: AWS Deployment Topology Selection`](../../adr/0003-aws-deployment-topology.md). Option B is formally approved as the production standard.

