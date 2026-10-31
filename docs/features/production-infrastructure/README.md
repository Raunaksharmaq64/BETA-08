# Production Infrastructure, AWS Deployment & Disaster Recovery
**Phase 13 Implementation Catalog**

## Overview
Phase 13 establishes the production-grade cloud infrastructure, container orchestration, network isolation, TLS ingress, automated backup/recovery, and operational monitoring for the RIGHT FIT Career Intelligence Platform.

### Core Architectural Decisions:
- **Topology**: Approved under **ADR-0003** as **Option B: EC2 Application Host + Amazon RDS PostgreSQL 16 Multi-AZ + Private Redis + S3 Object Storage**.
- **Network Isolation**: 3-Tier Multi-AZ VPC strictly sequestering PostgreSQL and Redis into Isolated Subnets with **ZERO public ingress or internet egress routes**.
- **Access Control**: Administrative server access is governed via **AWS Systems Manager Session Manager** with port 22 (SSH) completely blocked to the public internet.
- **Containerization**: Production multi-stage Dockerfiles executing as unprivileged non-root users (`appuser`, `nextjs`) with healthcheck gates and graceful signal handling (`SIGTERM`).
- **Disaster Recovery**: Validated backup and restore cycle with custom-format PostgreSQL dumps, SHA256 integrity checksums, continuous PITR, and S3 offsite replication ($RPO < 1\text{h}$, $RTO < 2\text{h}$).

---

## Document Index
1. [`architecture.md`](./architecture.md) &mdash; Overall infrastructure topology, component boundaries, and traffic flow.
2. [`aws-topology-adr.md`](./aws-topology-adr.md) &mdash; Evaluation matrix and formal selection of Option B.
3. [`network-and-security.md`](./network-and-security.md) &mdash; 3-Tier VPC, security group rules, and zero-trust perimeter.
4. [`containerization-guide.md`](./containerization-guide.md) &mdash; Multi-stage Dockerfiles, non-root users, and compose orchestration.
5. [`secrets-and-environment.md`](./secrets-and-environment.md) &mdash; AWS SSM Parameter Store, credential protection, and runtime injection.
6. [`database-and-rds.md`](./database-and-rds.md) &mdash; Amazon RDS PostgreSQL 16 Multi-AZ, storage encryption, and migration rules.
7. [`redis-and-celery.md`](./redis-and-celery.md) &mdash; In-memory broker, memory limits, eviction policies, and worker lifecycle.
8. [`s3-storage-and-lifecycle.md`](./s3-storage-and-lifecycle.md) &mdash; Private object storage, Block Public Access, presigned URLs, and lifecycle rules.
9. [`tls-and-nginx.md`](./tls-and-nginx.md) &mdash; Reverse proxy, SSL termination, security headers, and rate limiting.
10. [`monitoring-and-alerting.md`](./monitoring-and-alerting.md) &mdash; CloudWatch alarms, metrics, JSON logging, and zero-PII scrubbing.
11. [`backup-and-restore-runbook.md`](./backup-and-restore-runbook.md) &mdash; Step-by-step backup, checksumming, and isolated restore testing.
12. [`disaster-recovery-runbook.md`](./disaster-recovery-runbook.md) &mdash; RPO/RTO targets, failure scenarios, and disaster recovery procedures.
13. [`deployment-runbook.md`](./deployment-runbook.md) &mdash; Pre-flight migration checks, rolling container swap, and health-check gates.
14. [`rollback-runbook.md`](./rollback-runbook.md) &mdash; Automated rollback procedures, image tag rollbacks, and schema forward-fixing.
15. [`incident-response-guide.md`](./incident-response-guide.md) &mdash; Severity matrix, triage playbooks, and escalation paths.
16. [`cost-estimation.md`](./cost-estimation.md) &mdash; Itemized monthly AWS infrastructure cost estimation (\$180 – \$260/month).
17. [`production-release-checklist.md`](./production-release-checklist.md) &mdash; 25-point comprehensive pre-flight go-live checklist.

