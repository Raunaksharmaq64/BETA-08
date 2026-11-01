# RIGHT FIT — Server Commands

## Quick Fix if Ports are Blocked (`EADDRINUSE` / `WinError 10013`)
If a terminal throws port already in use, run this single line in PowerShell to instantly free all ports:
```powershell
Stop-Process -Id (Get-NetTCPConnection -LocalPort 8000, 3000, 8002 -ErrorAction SilentlyContinue).OwningProcess -Force -ErrorAction SilentlyContinue
```

---

## 1. One-Click Start (All Servers)
Double-click:
```cmd
start_servers.bat
```
(located in `c:\Users\Sahil\Desktop\manit\` or `c:\Users\Sahil\Desktop\manit\rightFIT\`)
*Note: `start_servers.bat` automatically frees occupied ports 8000, 3000, 8002 before launching!*

---

## 2. Start Backend (FastAPI — Port 8000)

```cmd
cd c:\Users\Sahil\Desktop\manit\rightFIT
python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
```

- API URL: http://localhost:8000
- Swagger Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health/live

---

## 3. Start Frontend (Next.js — Port 3000)

```cmd
cd c:\Users\Sahil\Desktop\manit\rightFIT\frontend
npm run dev
```

- Web App URL: http://localhost:3000
- Open in browser:
  - Homepage: http://localhost:3000
  - Canonical Opportunities: http://localhost:3000/opportunities
  - Job Sources Registry: http://localhost:3000/sources
  - Resume Intelligence: http://localhost:3000/resumes
  - Candidate Profile: http://localhost:3000/profile
  - Freelance Opportunities: http://localhost:3000/freelance
  - Startup Intelligence: http://localhost:3000/startups
  - Login / Register: http://localhost:3000/login

---

## 4. Startup Intelligence (Native or Satellite Port 8002)

- **Single-Instance Deployment (AWS / Production)**:
  Startup Intelligence is now natively integrated directly into the Core backend on Port 8000. When deploying to AWS, you do **not** need a separate EC2/ECS instance or port!

- **Optional Microservice Satellite (Port 8002)**:
```cmd
cd c:\Users\Sahil\Desktop\manit\rightFIT\services\startup_intelligence
python -m uvicorn main:app --host 127.0.0.1 --port 8002 --reload
```

- Service URL: http://localhost:8002
- Health Check: http://localhost:8002/health
- Swagger Docs: http://localhost:8002/docs
