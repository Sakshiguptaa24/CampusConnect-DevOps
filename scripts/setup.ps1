# ============================================
# CampusConnect - Setup Script
# ============================================

$root = Split-Path -Parent $PSScriptRoot
$nodePath = "$env:LOCALAPPDATA\Programs\node"
if (Test-Path $nodePath) {
    $env:Path = "$nodePath;$env:Path"
}

Write-Host "Installing Backend Requirements..." -ForegroundColor Cyan
cd "$root\backend"
python -m pip install -r requirements.txt

Write-Host "Installing Frontend Dependencies..." -ForegroundColor Cyan
cd "$root\frontend"
npm install

Write-Host "Setup Completed Successfully!" -ForegroundColor Green
