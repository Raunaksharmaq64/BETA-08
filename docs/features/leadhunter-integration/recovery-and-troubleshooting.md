# Recovery & Troubleshooting Runbook

## Failure Modes & Mitigations

### 1. LeadHunter Satellite Service Unreachable
- **Symptom**: `Circuit breaker OPEN` or `ConnectionRefusedError`.
- **System Behavior**: Core activates Degraded Service Mode. Cached local freelance opportunities remain fully browsable. The frontend displays an informative amber banner explaining that live scans are temporarily paused while maintaining all core platform operations.
- **Recovery**: Start or restart LeadHunter service on port 8001. After 30 seconds, Core probe will reset the circuit breaker to `CLOSED`.

### 2. Upstream Scraper Quota Exceeded (SerpApi / Apify)
- **Symptom**: LeadHunter returns HTTP 429 or empty scan results.
- **Mitigation**: Configure Apify fallback token in LeadHunter `api_config.py` or adjust scan batch sizes.

### 3. Recipient Suppression False Positive
- **Resolution**: Candidate or admin removes recipient from `outreach_suppression_list` table after verifying user consent.

