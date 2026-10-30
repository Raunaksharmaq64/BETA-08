# RIGHT FIT — Local Development & Deterministic Mocking Guide
**Version:** 1.0.0  
**Phase:** 2 — Contracts & Local Foundation  
**Status:** ACTIVE GUIDE  

---

## 1. Overview & Offline Guarantee

RIGHT FIT is designed to be fully developable and testable offline without requiring expensive third-party subscriptions or live API keys (OpenAI, Anthropic, Gemini, Apify, Google Maps, Reddit API).

In Phase 2, deterministic mock providers simulate all satellite microservice behavior:
- `backend/app/integrations/mock_providers.py`
  - `MockLeadHunterClient`
  - `MockStartupHunterClient`

---

## 2. Mock Simulation Modes

Both mock clients support five deterministic simulation modes configured via constructor:

```python
from backend.app.integrations.mock_providers import MockLeadHunterClient, MockStartupHunterClient

# 1. Success mode (returns 2 verified candidate leads/problems)
client = MockLeadHunterClient(mode="success")

# 2. Empty mode (returns 0 items for empty searches)
client = MockLeadHunterClient(mode="empty")

# 3. Validation error mode (simulates 422 Unprocessable Entity)
client = MockLeadHunterClient(mode="validation_error")

# 4. Outage mode (simulates 503 Service Unavailable)
client = MockLeadHunterClient(mode="unavailable")

# 5. Latency timeout mode (simulates 504 Gateway Timeout)
client = MockStartupHunterClient(mode="timeout")
```

---

## 3. Running the Test Suite Locally

The contract test suite verifies compliance with all envelopes, error schemas, service identity tokens, and satellite mock behaviors:

```bash
# From the project root (RIGHT FIT/):
python -m pytest backend/tests/contract -v
```

### Checking Test Coverage
```bash
python -m pytest backend/tests/contract --cov=contracts
```

**Result:** All 32 contract tests execute in <2.0 seconds with 99%+ statement coverage.

---

## 4. Running Core API Locally

To start the Core Career Engine locally with Uvicorn:

```bash
# Set PYTHONPATH to project root
set PYTHONPATH=%CD%;%CD%\backend

# Launch FastAPI server on port 8000
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Interactive documentation is immediately available at:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`
- Liveness Probe: `http://127.0.0.1:8000/health/live`
- Readiness Probe: `http://127.0.0.1:8000/health/ready`

