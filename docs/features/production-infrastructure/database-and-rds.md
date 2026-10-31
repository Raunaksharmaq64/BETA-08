# PostgreSQL Database Strategy & RDS Management

## 1. Production Database Specification
- **Engine**: PostgreSQL 16.3 on Amazon RDS.
- **Instance Sizing**: `db.t4g.medium` (2 vCPUs, 4GB RAM) with GP3 storage (50GB initial, autoscale to 500GB).
- **High Availability**: Multi-AZ standby deployment with synchronous replication.
- **Encryption**: AES-256 storage encryption powered by AWS KMS.
- **Network Placement**: Subnet group spanning Tier 3 Isolated Subnets with **no public accessibility** (`publicly_accessible = false`).

## 2. Security & Connection Constraints
- **SSL/TLS Enforcement**: The custom parameter group sets `rds.force_ssl = 1`, rejecting unencrypted plaintext client connections.
- **Connection URI**: Always specifies `sslmode=require`.
- **Connection Pooling**: FastAPI uses SQLAlchemy with an async connection pool configured for 20 connections (`pool_size=20`, `max_overflow=10`).
- **Query Timeout**: Hard limit of 30,000ms (`statement_timeout = 30000`) prevents runaway analytics queries from starving candidate requests.

## 3. Migration Safety & Deployment Rules
1. **Never Run Destructive Schema Changes**: Migrations that drop columns, drop tables, or rename active columns are strictly prohibited during operational deployments.
2. **Three-Phase Schema Evolution**:
   - *Phase 1 (Add)*: Add new nullable columns or tables. Deploy new code writing to both.
   - *Phase 2 (Backfill)*: Backfill historical data in background batch jobs.
   - *Phase 3 (Deprecate)*: Switch reads to new structure; archive legacy columns in a subsequent release.
3. **Pre-Flight Migration Gate**: The deployment script executes `alembic upgrade head` before container swap. If Alembic fails, the deployment halts immediately without disrupting running containers.

