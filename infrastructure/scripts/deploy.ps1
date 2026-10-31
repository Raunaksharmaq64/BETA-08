# ==============================================================================
# RIGHT FIT — Production Deployment Script (PowerShell for Windows)
# ==============================================================================
param(
    [string]$ReleaseTag = "latest",
    [string]$ComposeFile = "docker-compose.prod.yml",
    [string]$EnvFile = ".env.production"
)

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "RIGHT FIT — Initiating Production Deployment [Release: $ReleaseTag]" -ForegroundColor Cyan
Write-Host "======================================================================"

if (-not (Test-Path $EnvFile)) {
    Write-Host "Warning: $EnvFile not found. Using local .env fallback." -ForegroundColor Yellow
    if (Test-Path ".env") {
        $EnvFile = ".env"
    }
}

Write-Host "[1/4] Building production images..." -ForegroundColor Green
docker compose -f $ComposeFile build

Write-Host "[2/4] Starting production services..." -ForegroundColor Green
docker compose -f $ComposeFile up -d --remove-orphans

Write-Host "[3/4] Awaiting health confirmation..." -ForegroundColor Green
Start-Sleep -Seconds 10
docker compose -f $ComposeFile ps

Write-Host "[4/4] Executing smoke tests..." -ForegroundColor Green
python infrastructure/scripts/smoke_test.py "http://localhost:8000" "http://localhost:3000"

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "Deployment completed." -ForegroundColor Cyan

