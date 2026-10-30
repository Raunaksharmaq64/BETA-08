# RIGHT FIT — Server Commands

## 1. One-Click Start (All Servers)
```cmd
start_servers.bat
```

---

## 2. Start Backend (FastAPI — Port 8000)

### Windows Command Prompt (cmd.exe):
```cmd
cd c:\Users\Sahil\Desktop\manit\rightFIT
set PYTHONPATH=%CD%;%CD%\backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Windows PowerShell:
```powershell
cd c:\Users\Sahil\Desktop\manit\rightFIT
$env:PYTHONPATH = "$PWD;$PWD/backend"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
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

