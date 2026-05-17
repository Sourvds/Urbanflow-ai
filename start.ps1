# UrbanFlow AI — local startup (no Docker required)
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "Starting UrbanFlow AI..." -ForegroundColor Cyan

# Backend
$backend = Join-Path $root "backend"
if (-not (Test-Path (Join-Path $backend "venv"))) {
    Write-Host "Creating Python venv..."
    python -m venv (Join-Path $backend "venv")
    & (Join-Path $backend "venv\Scripts\pip") install -r (Join-Path $backend "requirements.txt")
    & (Join-Path $backend "venv\Scripts\pip") install bcrypt==4.0.1
}

$db = Join-Path $backend "urbanflow.db"
if (-not (Test-Path $db)) {
    Write-Host "Seeding database (first run)..."
    Push-Location $backend
    $env:DATABASE_URL = "sqlite:///./urbanflow.db"
    & .\venv\Scripts\python scripts\seed_data.py
    Pop-Location
}

Write-Host "Backend -> http://localhost:8000/docs"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backend'; `$env:DATABASE_URL='sqlite:///./urbanflow.db'; .\venv\Scripts\uvicorn app.main:app --reload --port 8000"

Start-Sleep -Seconds 2

Write-Host "Frontend -> http://localhost:5173"
$frontend = Join-Path $root "frontend"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$frontend'; npm run dev"

Write-Host ""
Write-Host "Login: admin@urbanflow.ai / UrbanFlow2026!" -ForegroundColor Green
