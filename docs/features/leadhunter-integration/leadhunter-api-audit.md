# LeadHunter AI API Audit & Inventory

## Overview
Forensic audit of the independent LeadHunter AI repository (`C:\Users\Sahil\Desktop\manit\ai agents`, commit `30d5695`).

## Endpoints Inventory

| Endpoint | Method | Purpose | Auth Required | Parameters / Body | Response Schema |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `/health` | GET | System status & DB probe | No | None | `{"status": "healthy", "database": "healthy"}` |
| `/api/leads/search` | POST | Trigger Google Maps scan | Yes (Bearer/Cookie) | `{query, city, max_results, deep_scan}` | `{"success": true, "task_id": "...", "leads": [...]}` |
| `/api/leads` | GET | List saved leads | Yes | `city, priority, q, page, per_page` | `{"success": true, "leads": [...]}` |
| `/api/leads/{id}/audit` | POST | Website technical health check | Yes | `lead_id` | `{"dns": true, "ssl": true, "status": 200}` |
| `/api/leads/{id}/scan-email` | POST | Email contact extraction | Yes | `lead_id` | `{"email": "...", "confidence": 0.85}` |

## Authentication & Security
- Uses JWT HS256 tokens (`access_token` cookie or `Authorization: Bearer <token>`).
- CSRF validation on cookie-based state-changing requests (Origin/Referer checking).
- Passwords hashed using Werkzeug `scrypt`/`pbkdf2`.

## Data Models
- `LeadModel` (`leads` table): place_id, name, phone, address, website, rating, reviews, category, city, priority, is_broken_website, email, audit_data.
- Owned completely by LeadHunter AI; no direct Core Career Engine database connection permitted.

