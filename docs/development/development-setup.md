# Development Setup Guide

- **Title:** RIGHT FIT Local Development Setup
- **Purpose:** Step-by-step instructions for engineering onboarding, dependency prerequisites, and environment initialization.
- **Status:** DRAFT / ARCHITECTURE SETUP
- **Owner:** Engineering Team (TBD)
- **Last Updated:** 2026-10-30

---

## 1. System Prerequisites
Ensure the following developer tools are installed on your workstation:
- **Node.js:** v20.x or v22.x LTS (`node -v`)
- **Python:** v3.11+ (`python --version`)
- **Docker & Docker Compose:** Latest stable version (`docker compose version`)
- **Git:** 2.40+ (`git --version`)

## 2. Workspace Initialization
1. Navigate to the project root:
   ```bash
   cd rightFIT
   ```
2. Copy environment configuration:
   ```bash
   cp .env.example .env
   cp frontend/.env.example frontend/.env.local
   cp backend/.env.example backend/.env
   ```
3. Populate necessary development keys (Google Gemini API key, database credentials).

## 3. Running via Docker Compose (Recommended)
```bash
# Launch entire multi-service development stack
docker compose up -d

# Verify all containers are healthy
docker compose ps
```

## 4. Running Standalone (Local Native)
### Backend:
```bash
cd backend
python -m venv .venv
# On Windows: .venv\Scripts\activate | On Unix: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend:
```bash
cd frontend
npm install
npm run dev
```

## 5. Open Questions & TBDs
- [TBD] Pre-commit hook automatic installation script (`scripts/development/setup-hooks.sh`).

