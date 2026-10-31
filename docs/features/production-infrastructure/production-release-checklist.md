# Production Release Checklist (25-Point Gate)

## Security & Access
- [x] 1. Zero secrets in Git repository or committed Docker images.
- [x] 2. PostgreSQL and Redis have zero public ingress (isolated subnet tier).
- [x] 3. Database parameter group enforces `rds.force_ssl = 1`.
- [x] 4. Edge Nginx enforces HTTPS (301 redirect) and HSTS.
- [x] 5. Modern TLS (1.2, 1.3) with strong ciphers enabled.
- [x] 6. Rate limiting zones active for general API and auth endpoints.
- [x] 7. S3 buckets have Block Public Access enabled on all 4 flags.
- [x] 8. Pre-signed URLs expire within 15 minutes.
- [x] 9. Port 22/SSH is closed; access via AWS Systems Manager Session Manager.

## Container & Compute Hardening
- [x] 10. Multi-stage Docker builds strip compilers from runtime images.
- [x] 11. Containers execute as unprivileged non-root users (`appuser`, `nextjs`).
- [x] 12. Resource limits (CPU/Memory) configured in Compose.
- [x] 13. Signal handling (`STOPSIGNAL SIGTERM`) configured for graceful drain.
- [x] 14. Docker health check probes active on all services.

## Database & Storage Resiliency
- [x] 15. Amazon RDS Multi-AZ enabled for synchronous standby failover.
- [x] 16. Automated daily backups configured with 30-day retention.
- [x] 17. Disaster recovery restore tested into isolated target database.
- [x] 18. Pre-flight database migration gate active in deployment script.
- [x] 19. S3 lifecycle policies configured for Standard-IA and Glacier transitions.

## Observability & Operations
- [x] 20. Structured JSON logging configured with zero PII/credential scrubbing.
- [x] 21. CloudWatch alarms configured for CPU, Storage, and Connections.
- [x] 22. Automated rollback script tested and verified.
- [x] 23. Post-deployment smoke test suite executes on release.
- [x] 24. Incident triage and escalation runbooks documented.
- [x] 25. Explicit product owner approval obtained prior to live launch.

