# ============================================
# CampusConnect - Local Development Launcher
# ============================================

$root = Split-Path -Parent $PSScriptRoot
$nodePath = "$env:LOCALAPPDATA\Programs\node"
if (Test-Path $nodePath) {
    $env:Path = "$nodePath;$env:Path"
}

Write-Host "================================================" -ForegroundColor Cyan
Write-Host " CampusConnect — Starting Local Dev Environment " -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

# 1. Start Backend in separate window
Write-Host "Starting FastAPI Backend on http://localhost:8000..." -ForegroundColor Green
$backendProcess = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root\backend'; python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000" -PassThru

# 2. Start Frontend in separate window
Write-Host "Starting Vite React Frontend on http://localhost:5173..." -ForegroundColor Green
$frontendProcess = Start-Process powershell -ArgumentList "-NoExit", "-Command", "`$env:Path = '$nodePath;' + `$env:Path; cd '$root\frontend'; npm run dev" -PassThru

Write-Host "`nCampusConnect is booting up!" -ForegroundColor Yellow
Write-Host "  Backend API:  http://localhost:8000" -ForegroundColor White
Write-Host "  Interactive:  http://localhost:8000/docs" -ForegroundColor White
Write-Host "  Frontend App: http://localhost:5173" -ForegroundColor White
Write-Host "`nDemo Credentials:" -ForegroundColor Cyan
Write-Host "  Admin:   admin@campusconnect.com / Admin@123" -ForegroundColor White
Write-Host "  Student: student@campusconnect.com / Student@123" -ForegroundColor White
