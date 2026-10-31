# Saved Searches & Alert Subscriptions

## 1. Overview & Capabilities

Candidates can save complex filter queries and subscribe to automated notifications when new matching jobs are discovered and normalized into the platform.

### Supported Notification Frequencies
- `INSTANT`: Evaluates newly ingested opportunities immediately upon ingestion run completion.
- `DAILY`: Batches matching opportunities into a daily digest (minimum 23 hours between deliveries).
- `WEEKLY`: Summarizes weekly discoveries (minimum 7 days between deliveries).
- `NEVER`: Retains saved query parameters without generating notifications.

---

## 2. Data Model

The `saved_searches` table stores candidate search subscriptions:
- `id`: UUID primary key
- `user_id`: Foreign key to `users.id` (CASCADE)
- `name`: User-friendly label (e.g. "Remote Python Roles")
- `query_json`: Serialized free-text query object
- `filters_json`: Serialized filter constraints (role, location, remote, salary, etc.)
- `alert_enabled`: Boolean flag enabling or pausing notifications
- `alert_frequency`: Notification cadence string
- `last_notified_at`: UTC timestamp of most recent successful notification delivery
- `created_at`, `updated_at`: UTC timestamps

---

## 3. REST API Specifications

- `POST /api/v1/saved-searches`: Creates a new search subscription.
- `GET /api/v1/saved-searches`: Lists all saved searches with frequency and last notified status.
- `PATCH /api/v1/saved-searches/{id}`: Modifies search name, filters, or notification frequency.
- `DELETE /api/v1/saved-searches/{id}`: Deletes the subscription and removes active alerts.
- `POST /api/v1/saved-searches/run-alerts`: Triggers the background alert evaluation worker.

