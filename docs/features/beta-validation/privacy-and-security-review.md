# Security, Sandbox Containment & Privacy Audit

**Document ID:** RF-SPEC-1408  
**Phase:** 14 — Beta Testing & Product Validation  
**Status:** Approved  

---

## 1. Security Architecture & Threat Model

Phase 14 verifies that production security controls deployed during Phase 13 remain effective and non-bypassable during beta user interactions.

```mermaid
flowchart TD
    Client["Beta User Web Browser"] -->|HTTPS (TLS 1.2/1.3)| NGINX["Nginx Ingress Proxy"]
    NGINX -->|Rate Limiting (30r/s API, 5r/s Auth)| DockerNet["Isolated Ingress Network"]
    DockerNet --> Backend["FastAPI Backend (Non-Root User: rightfit 10001)"]
    Backend -->|Dual-Network Segregation| DBNet["Isolated Internal Network"]
    DBNet --> DB[("PostgreSQL 16 (No Public IP)")]
    DBNet --> Redis[("Redis 7.2 (No Public IP)")]
```

---

## 2. Core Security Audits & Findings

### 1. Zero Hardcoded Credentials & Secret Scanning
- Automated scanner verified 0 API keys, passwords, or production connection strings committed to Git.
- Database passwords and JWT secret keys are loaded exclusively through environment variables (`os.environ`).

### 2. Network Isolation & Database Ingress
- PostgreSQL and Redis containers bind exclusively to `rightfit-internal-net` (no external host port forwarding in production Compose).
- Database credentials enforce SSL requirement (`sslmode=require`).

### 3. Non-Root Container Execution
- All Dockerfiles (`backend/Dockerfile`, `frontend/Dockerfile`, `services/leadhunter/Dockerfile`, `services/startup_intelligence/Dockerfile`) enforce non-root user execution (`USER rightfit:rightfit` with UID 10001).
- System root filesystem access is prevented inside all application containers.

### 4. PII Minimization & Resume Storage
- Resumes uploaded for parsing are stored in private S3 buckets using server-side encryption (`AES-256`).
- Candidate names, email addresses, and phone numbers are stripped from diagnostic error logs.
- Beta telemetry is scheduled for automatic hard deletion after 90 days.

---

## 3. Security Compliance Checklist

| Safeguard | Requirement | Audit Result | Status |
|:---|:---|:---|:---|
| Ingress TLS | Enforce TLS 1.2 / 1.3 only | Validated in `rightfit.conf` | **PASS** |
| Rate Limiting | 30r/s per IP for general APIs, 5r/s for Auth | Active in Nginx `limit_req_zone` | **PASS** |
| Access Control | Role-based JWT validation with expiration | Verified on all `/api/v1/*` routes | **PASS** |
| Sandboxing | Independent satellite services (LeadHunter / Startups) | Run in isolated networks | **PASS** |
| Data Deletion | Self-serve consent withdrawal & purge | Operational in `POST /api/v1/beta/consent/withdraw` | **PASS** |

