# Incident Response Guide

## 1. Incident Severity Classification
- **P1 (Critical Outage)**: Core API or Web Frontend completely unavailable to users; data corruption detected. Response target: < 15 minutes.
- **P2 (Degraded Experience)**: Core search operational, but one satellite or resume upload failing. Response target: < 1 hour.
- **P3 (Minor Issue)**: Non-critical styling glitch or minor administrative report defect. Response target: Next business day.

## 2. Escalation & Triage Playbook
1. Check CloudWatch alarms and Nginx access logs:
   ```bash
   tail -n 100 /var/log/nginx/access.log | grep -E '"status": "(500|502|503)"'
   ```
2. Inspect container status:
   ```bash
   docker compose -f docker-compose.prod.yml ps
   docker compose -f docker-compose.prod.yml logs --tail=100 backend
   ```
3. Restart degraded services:
   ```bash
   docker compose -f docker-compose.prod.yml restart backend
   ```

