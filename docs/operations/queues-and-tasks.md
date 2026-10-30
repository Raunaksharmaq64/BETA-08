# RIGHT FIT — Redis Queues & Asynchronous Task Envelope Architecture
**Version:** 1.0.0  
**Phase:** 2 — Contracts & Local Foundation  
**Status:** ACTIVE GOVERNANCE  

---

## 1. Asynchronous Architecture & Queue Namespaces

RIGHT FIT uses Redis 7 as the unified background task broker, separating workloads into strictly partitioned queue namespaces to prevent heavy background crawling from starving interactive user requests.

```
                      [ Redis Broker ]
                             │
     ┌───────────────────────┼───────────────────────┐
     ▼                       ▼                       ▼
[ career_tasks ]       [ lead_tasks ]          [ startup_tasks ]
 (Resume parsing,       (Business discovery,    (Reddit / HN crawlers,
  ATS job sync)          Website audits)         Pain-point extraction)
                             │
                             ▼
                    [ notification_tasks ]
                     (Transactional email,
                      Status alerts)
```

### 1.1 Dedicated Queue Allocation

| Queue Name | Worker Affinity | Priority | Description |
| :--- | :--- | :--- | :--- |
| `career_tasks` | `backend/app/workers` | High | Interactive candidate workflows, resume parsing, ATS sync, fit scoring. |
| `lead_tasks` | `service-leadhunter` | Normal | Business discovery, Google Maps crawling, deep website audits. |
| `startup_tasks` | `service-startup-intel`| Normal | Community crawling (Reddit, GitHub, HN), problem clustering. |
| `notification_tasks` | Shared | Normal | User emails, application status notifications, pitch dispatches. |

---

## 2. Universal Task Envelope Contract (`TaskEnvelope`)

All messages placed onto Redis task queues must serialize according to the `TaskEnvelope` contract:

```json
{
  "task_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "task_type": "lead.discovery.scheduled",
  "schema_version": "1.0",
  "correlation_id": "7a9e223b-55c1-4ef8-a28b-b89280dfbb84",
  "created_at": "2026-10-31T00:50:00Z",
  "max_retries": 3,
  "timeout_seconds": 300,
  "payload": {
    "query": "Dentists",
    "city": "Austin, TX",
    "max_results": 20
  }
}
```

### 2.1 Field Specifications

| Field | Type | Description |
| :--- | :--- | :--- |
| `task_id` | `UUID string` | Unique identifier for this task execution instance. |
| `task_type` | `string` | Dot-separated task descriptor (e.g., `resume.parse`, `lead.discovery`). |
| `schema_version`| `string` | Payload schema version (`"1.0"`). |
| `correlation_id`| `UUID string` | Request ID that initiated the task for end-to-end tracing. |
| `created_at` | `datetime (UTC)` | Timestamp when the message was dispatched into Redis. |
| `max_retries` | `integer (>= 0)` | Maximum retry attempts on transient network or third-party errors. |
| `timeout_seconds`| `integer (>= 1)`| Worker timeout deadline before task is forcibly aborted. |
| `payload` | `dict[str, Any]` | Typed arguments specific to `task_type`. |

---

## 3. Retries, Timeouts & Dead Letter Queue (DLQ)

1. **Exponential Backoff:** When a task encounters a transient error (e.g. rate limit or temporary network partition), retries occur with exponential backoff:
   $$\text{delay} = 2^{\text{attempt}} \times 5\text{ seconds}$$
2. **Hard Timeout Enforcement:** Tasks exceeding `timeout_seconds` are marked `FAILED` and worker resources reclaimed.
3. **Dead Letter Queue (DLQ):** Tasks that exhaust `max_retries` are moved to `dlq:<queue_name>` (e.g., `dlq:career_tasks`) for operator inspection without blocking queue progress.

