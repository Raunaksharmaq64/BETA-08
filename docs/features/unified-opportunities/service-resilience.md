# Service Failure Resilience & Circuit Breaker Degradation

## 1. Resilience Philosophy
External satellite services (LeadHunter AI and Startups-problems-hunter) run independently. Network partitions, timeouts, or restarts must NEVER cause the Core Career Engine or Unified Dashboard to fail.

## 2. Ingestion Satellites Circuit Breakers
Both adapters (`leadhunter_adapter` and `startup_adapter`) utilize PyBreaker circuit breakers:
- **Threshold**: 5 consecutive failures
- **Timeout**: 60 seconds reset timeout
- **Fallback**: Returns cached local records from PostgreSQL and reports `DEGRADED` status in metadata.

## 3. Degradation States
1. `ALL_SERVICES_AVAILABLE`: All circuit breakers are in `CLOSED` state; satellites are healthy.
2. `PARTIAL_RESULTS`: One or more satellites have tripped their circuit breakers to `OPEN`.
   - Core returns locally ingested database records.
   - Response envelope sets `is_partial_results: true`.
   - Frontend displays amber warning banner explaining the degradation without blocking user browsing.
3. `ONE_OR_MORE_SERVICES_UNAVAILABLE`: Satellite unreachable; aggregation completes successfully using available operational modules.

