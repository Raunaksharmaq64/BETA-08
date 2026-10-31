# Monitoring, Logging & Alerting Guide

## 1. Observability Topology
- **Structured JSON Logging**: Nginx and FastAPI output single-line JSON logs capturing timestamp, client IP, method, URI, status code, latency, and request ID.
- **Log Scrubbing**: Log formatters strictly redact passwords, JWT tokens, candidate resume text, and API keys.
- **Central Log Group**: Logs stream to Amazon CloudWatch under `/aws/rightfit/production` with 30-day retention.

## 2. Actionable Operational Alarms
Alarms publish directly to Amazon SNS topic `rightfit-production-operational-alerts`:
1. **EC2 High CPU**: CPUUtilization > 85% for 10 consecutive minutes.
2. **RDS Critical Storage**: FreeStorageSpace < 5GB remaining.
3. **Database Connection Starvation**: DatabaseConnections > 85 active connections.
4. **Elevated 5xx Rate**: HTTP 5xx responses > 2% of total traffic over 5 minutes.
5. **API Latency Degradation**: $P_{95}$ response time > 1,500ms over 5 minutes.
6. **Celery Task Backlog**: Redis queue length > 500 unprocessed tasks.

