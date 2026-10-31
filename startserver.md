# RIGHT FIT — Server Commands

## 1. One-Click Start (All Servers)
```cmd
start_servers.bat
```

---

## 2. Start Backend (FastAPI — Port 8000)

### Universal Command (PowerShell / CMD / Terminal):
```powershell
cd c:\Users\Sahil\Desktop\manit\rightFIT
python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
```

- API URL: http://localhost:8000
- Swagger Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health/live

---

## 3. Start Frontend (Next.js — Port 3000)

### Option A: Ready-to-run Next.js Frontend
```cmd
cd "c:\Users\Sahil\Desktop\manit\ai agents\frontend"
npm run dev
```

### Option B: Core Project Frontend
```cmd
cd "c:\Users\Sahil\Desktop\manit\rightFIT\frontend"
npm install
npm run dev
```

- Web App URL: http://localhost:3000

---

## 4. Run Contract Tests
```powershell
cd c:\Users\Sahil\Desktop\manit\rightFIT
python -m pytest backend/tests/contract -v
```

Tareeqa 2 (Manual Terminal Se):

Terminal 1 — Backend:

cd c:\Users\Sahil\Desktop\manit\rightFIT
python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload

erminal 2 — Frontend:

cmd
cd c:\Users\Sahil\Desktop\manit\rightFIT\frontend
npm run dev

Ab browser me http://localhost:3000 kholein — aapko poora visual dashboard live dikhega!