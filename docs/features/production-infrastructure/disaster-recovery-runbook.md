# Disaster Recovery Runbook

## 1. RPO and RTO Targets
- **Recovery Point Objective (RPO)**: **< 1 hour** (Guaranteed by continuous RDS write-ahead log (WAL) archiving and daily offsite binary dumps).
- **Recovery Time Objective (RTO)**: **< 2 hours** (Automated Multi-AZ primary failover completes in < 120 seconds; complete regional infrastructure rebuild via Terraform completes in < 45 minutes).

## 2. Failure Scenarios & Recovery Procedures
1. **Scenario A: Primary Database AZ Outage**
   - *Impact*: Amazon RDS primary instance in `us-east-1a` fails.
   - *Automated Action*: RDS Multi-AZ automatically detects failure, switches DNS endpoint to synchronous standby in `us-east-1b` within 60–120s.
   - *Engineer Action*: No data restore required. Verify backend reconnection pool re-established.
2. **Scenario B: Catastrophic Host Failure (EC2)**
   - *Engineer Action*: Execute `terraform apply -target=aws_instance.app_server`. Bootstrap script automatically initializes Docker and mounts environment from SSM Parameter Store.
3. **Scenario C: Accidental Data Corruption or Destructive Query**
   - *Engineer Action*: Use Amazon RDS Point-In-Time Restore (PITR) to restore database to 5 minutes prior to incident event.

