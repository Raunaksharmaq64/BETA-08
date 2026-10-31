# Monthly AWS Cost Estimation

## 1. Itemized Cost Breakdown (Option B Topology)
Calculated based on standard AWS US East (N. Virginia) pricing:

| Resource | Sizing & Specifications | Estimated Monthly Cost |
| :--- | :--- | :--- |
| **EC2 Workload Host** | `t4g.xlarge` (4 vCPU, 16GB RAM ARM64 Graviton) | \$97.00 |
| **EBS Root Volume** | 60GB GP3 SSD (3,000 IOPS, 125 MB/s) | \$4.80 |
| **Amazon RDS PostgreSQL** | `db.t4g.medium` Multi-AZ (2 vCPU, 4GB RAM) | \$105.00 |
| **RDS Storage & Backups** | 50GB GP3 + 50GB Backup retention | \$7.50 |
| **NAT Gateway** | Single AZ NAT Gateway + 30GB Data Processing | \$35.00 |
| **Amazon S3 Storage** | 20GB Resumes, Reports & Backups | \$0.50 |
| **Amazon CloudWatch** | Logs ingestion (5GB), Metric Alarms | \$6.00 |
| **Data Transfer Egress** | ~50GB outbound user traffic | \$4.50 |
| **Total Estimated Cost** | **Fully Managed Multi-AZ Infrastructure** | **\$260.30 / month** |

*Note: In single-AZ staging or dev tiers, disabling RDS Multi-AZ reduces total cost to ~\$150.00 / month.*

