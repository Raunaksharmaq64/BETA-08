# Independent Service Deployment Guide
## Workstream K Specification

- **Module:** `startup-intelligence`
- **Repository:** `c:\Users\Sahil\Desktop\manit\Startups-problrms-hunter`
- **Runtime:** Python 3.13 / FastAPI / Uvicorn

---

## 1. Architecture Boundaries

The `Startups-problrms-hunter` service operates as a completely autonomous microservice:
- **No Shared Database**: Owns its local storage in `data/leads.json` and does not query or write to the Core PostgreSQL database.
- **Dedicated Port**: Binds to port `8002` (configurable via `PORT` environment variable).
- **Service Identity**: Authenticates Core requests via `INTERNAL_SERVICE_KEY`.

---

## 2. Environment Configuration (`.env`)

```ini
# Server Port (configured for Hybrid Architecture coexistence)
PORT=8002

# Internal Service Secret for Core-to-Service REST authentication
INTERNAL_SERVICE_KEY=rightfit_internal_shared_secret_key_123

# Google Gemini AI Studio API Key (for semantic analysis & pitch generation)
GEMINI_API_KEY=your_gemini_api_key_here

# Google Search API Key (Serper.dev)
SERPER_API_KEY=your_serper_api_key_here

# B2B Email Search Keys (Hunter.io / Tomba.io - Optional)
HUNTER_API_KEY=
TOMBA_KEY=
TOMBA_SECRET=

# Technographics API (Wappalyzer - Optional)
WAPPALYZER_API_KEY=

# Resend API Key (Optional)
RESEND_API_KEY=your_resend_api_key_here
RESEND_SENDER_EMAIL=onboarding@resend.dev
```

---

## 3. Launch Commands

### Standalone Manual Start
```powershell
cd "c:\Users\Sahil\Desktop\manit\Startups-problrms-hunter"
python -m uvicorn main:app --host 127.0.0.1 --port 8002 --reload
```

### Health Verification
```powershell
curl http://localhost:8002/health
```

Expected output:
```json
{"status":"healthy","service":"startup-intelligence","version":"1.0.0","storage":"json","records_count":598}
```

