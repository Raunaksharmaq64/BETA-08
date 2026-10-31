# ==============================================================================
# RIGHT FIT — Production Rollback Script (PowerShell for Windows)
# ==============================================================================
param(
    [string]$ComposeFile = "docker-compose.prod.yml"
)

Write-Host "======================================================================" -ForegroundColor Red
Write-Host "RIGHT FIT — Initiating Production Rollback" -ForegroundColor Red
Write-Host "======================================================================"

Write-Host "[1/2] Restarting existing stable containers..." -ForegroundColor Yellow
docker compose -f $ComposeFile restart

Write-Host "[2/2] Checking container recovery status..." -ForegroundColor Yellow
Start-Sleep -Seconds 5
docker compose -f $ComposeFile ps

Write-Host "Rollback completed." -ForegroundColor Green

