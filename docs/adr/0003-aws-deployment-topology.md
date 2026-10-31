# ADR-0003: AWS Deployment Topology Selection

## Status
**ACCEPTED** (Date: 2026-10-31)

## Context
RIGHT FIT is an AI-powered Career and Opportunity Intelligence Platform requiring production deployment infrastructure on Amazon Web Services (AWS).
The system encompasses:
- Unified Next.js 16 web application (`frontend`).
- Core Career Engine FastAPI backend (`backend`).
- Celery background workers for snapshot aggregations and scrapers (`worker`).
- Autonomous LeadHunter freelance engine (`service-leadhunter`).
- Autonomous Startup Intelligence pain-point miner (`service-startup-intelligence`).
- Central PostgreSQL database containing 62 relational tables across Core and satellite schemas.
- In-memory Redis cache and task queue broker.
- Candidate resume and interview report object storage.

We evaluated three architectural topologies against security, monthly operating cost, operational complexity, scalability, reliability, and disaster recovery.

---

## Topology Evaluation Matrix

| Criterion | Option A: Single EC2 with Docker Compose | Option B: EC2 Workload Host + Managed RDS Multi-AZ + Private Redis (Selected) | Option C: Container-Oriented ECS/Fargate + ALB + Multi-AZ RDS + ElastiCache |
| :--- | :--- | :--- | :--- |
| **Estimated Monthly Cost** | \$60 – \$90 / month | **\$180 – \$260 / month** | \$450 – \$750 / month |
| **Operational Complexity** | Low (Single VM) | **Moderate (Balanced)** | High (Multiple managed abstractions) |
| **Database Durability** | Self-managed disk snapshots; manual recovery | **Automated Multi-AZ failover, 30-day continuous PITR** | Automated Multi-AZ failover, 30-day continuous PITR |
| **Security & Network Isolation** | Docker bridge networks on single host | **3-Tier VPC with physically isolated DB subnets** | 3-Tier VPC with micro-segmented security groups |
| **Compute Scalability** | Vertical only (Resizing EC2) | **Vertical compute with stateless horizontal migration path** | Horizontal auto-scaling container tasks |
| **Zero-Downtime Deployment** | Rolling container restart via Docker Compose | **Rolling container restart + managed DB connection pooling** | Rolling task replacement via AWS ALB target groups |
| **Disaster Recovery (RTO/RPO)** | RTO: 4 hours, RPO: 24 hours | **RTO: < 2 hours, RPO: < 1 hour** | RTO: < 30 mins, RPO: < 15 mins |

---

## Decision

We select **Option B (EC2 Application Host with Docker Compose + Managed Amazon RDS PostgreSQL Multi-AZ + Private Redis + S3 Object Storage)** as the authoritative production architecture for RIGHT FIT Phase 13.

### Justification:
1. **Database Reliability is Non-Negotiable**: RIGHT FIT manages 62 tables containing candidate resumes, identity credentials, verification ledgers, and audited compensation observations. Running PostgreSQL on a self-managed EBS disk without automated continuous point-in-time recovery (Option A) introduces unacceptable operational risk of data loss.
2. **Cost-to-Value Optimum**: Option B delivers 99.95% database availability, automated failover, and KMS encryption for ~$200/month, compared to Option C which incurs significant baseline costs (~$500+/month) for ALB, NAT gateways across multiple AZs, Fargate task minimums, and ElastiCache cluster nodes before significant candidate traffic arrives.
3. **Smooth Evolution Path**: Because all applications are containerized using standard, minimal Dockerfiles and decoupled via environment variables, migrating from Option B to Option C as traffic scales past 50,000 monthly active users requires zero application code changes—only updating the IaC compute definition from EC2 to ECS Task Definitions.

---

## Consequences

### Positive:
- High data durability with Amazon RDS automated backups, automated point-in-time recovery (PITR), and Multi-AZ standby replication.
- Zero public ingress to PostgreSQL or Redis: both reside in Tier 3 Isolated Subnets with no internet gateway route.
- Application compute runs cost-effectively on a single ARM64 Graviton EC2 instance (`t4g.xlarge`) orchestrating services with non-root Docker Compose.
- Access to instance is secured via AWS Systems Manager Session Manager; port 22 (SSH) is completely closed to the internet.

### Negative / Trade-offs:
- Compute capacity is bounded by the EC2 instance size; scaling application traffic requires resizing the instance or migrating to an ECS cluster.
- In-memory Redis runs on the application host with persistence (`appendonly yes`) rather than a multi-node ElastiCache cluster during initial launch.

---

## Approval
- **Status:** Formally Accepted
- **Principal Architect:** Senior AWS Solutions Architect & DevOps Lead
- **Related Documents:**
  - [`docs/features/production-infrastructure/architecture.md`](../features/production-infrastructure/architecture.md)
  - [`docs/features/production-infrastructure/network-and-security.md`](../features/production-infrastructure/network-and-security.md)
  - [`infrastructure/terraform/`](../../infrastructure/terraform/)

