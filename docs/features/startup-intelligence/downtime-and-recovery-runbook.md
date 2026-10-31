# Downtime & Recovery Runbook
## Workstream L Specification

- **Module:** `startup-intelligence`
- **Fault Tolerance:** Circuit Breaker, Exponential Backoff, Degraded Mode

---

## 1. Failure Scenarios & System Response

| Failure Scenario | System Detection | User Impact | Core System Behavior |
|---|---|---|---|
| **Satellite Service Down (Port 8002 Unreachable)** | Connection refused on HTTP client. | Amber warning banner shown on `/startups`. | Circuit Breaker trips to `OPEN` after 3 attempts. Core serves cached opportunities from database. |
| **Authentication Rejected (HTTP 401/403)** | `StartupIntelligenceAuthError` raised. | Scan fails with clear error. | Logged as security alert. Circuit breaker does not spam retries. |
| **Upstream Scraper Latency (> 10s)** | Read timeout triggered. | Scan returns degraded message. | Jittered exponential backoff attempt (max 2 retries). Fast-fails if timeout persists. |
| **Service Restarts & Recovers** | Probe succeeds in `HALF_OPEN` state. | Warning banner automatically clears. | Circuit state resets to `CLOSED`, failure counter resets to 0. |

---

## 2. Troubleshooting Steps

1. **Verify Satellite Process**:
   ```powershell
   Get-Process -Name python | Where-Object { $_.CommandLine -like "*main:app*" }
   ```
2. **Check Port 8002 Binding**:
   ```powershell
   netstat -ano | findstr :8002
   ```
3. **Inspect Upstream Logs**:
   Look at `Startups-problrms-hunter` terminal logs or query `http://localhost:8002/health`.
4. **Reset Circuit Breaker**:
   The circuit breaker automatically probes recovery after 30 seconds without requiring a server reboot.

