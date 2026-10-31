# Network & Security Architecture

## 1. Multi-Tier VPC Segmentation
The dedicated VPC (`10.0.0.0/16`) enforces strict network zoning across two Availability Zones (`us-east-1a`, `us-east-1b`):

| Subnet Tier | CIDR Blocks | Route Table Destination | Components |
| :--- | :--- | :--- | :--- |
| **Tier 1: Public Ingress** | `10.0.1.0/24`<br>`10.0.2.0/24` | `0.0.0.0/0` &rarr; Internet Gateway (`igw`) | Nginx Ingress Proxy, NAT Gateway |
| **Tier 2: Private App** | `10.0.10.0/24`<br>`10.0.11.0/24` | `0.0.0.0/0` &rarr; NAT Gateway (`nat-gw`) | EC2 Container Host, Next.js, FastAPI, Celery |
| **Tier 3: Isolated DB** | `10.0.20.0/24`<br>`10.0.21.0/24` | **Local VPC only** (No Default Route) | Amazon RDS PostgreSQL Multi-AZ |

## 2. Security Group Firewall Matrix

```
[Public Internet]
       │ (Port 80/443)
       ▼
┌──────────────────┐
│  ALB / NGINX SG  │
└────────┬─────────┘
         │ (Port 3000, 8000)
         ▼
┌──────────────────┐
│   APP TIER SG    │
└────┬────────┬────┘
     │        │
     │        │ (Port 6379)
     │        ▼
     │   ┌──────────────┐
     │   │   REDIS SG   │
     │   └──────────────┘
     │ (Port 5432)
     ▼
┌──────────────────┐
│   RDS POSTGRES   │
└──────────────────┘
```

### Explicit Rules:
1. **`sg_alb`**:
   - Ingress: `TCP 80` (ACME & redirect), `TCP 443` (TLS) from `0.0.0.0/0`.
   - Egress: Allowed to `sg_app`.
2. **`sg_app`**:
   - Ingress: `TCP 3000` (Next.js), `TCP 8000` (FastAPI) strictly from `sg_alb`.
   - Egress: `TCP 5432` to `sg_rds`, `TCP 6379` to `sg_redis`, `TCP 443` to internet via NAT Gateway.
3. **`sg_rds`**:
   - Ingress: `TCP 5432` strictly from `sg_app`.
   - Egress: None.
4. **`sg_redis`**:
   - Ingress: `TCP 6379` strictly from `sg_app`.
   - Egress: None.

## 3. Zero-SSH Administrative Access Policy
- Ingress on port 22 is completely blocked.
- Shell access and maintenance are conducted exclusively through **AWS Systems Manager (SSM) Session Manager**, which authenticates via IAM, logs all interactive commands to CloudWatch, and requires multi-factor authentication (MFA).

