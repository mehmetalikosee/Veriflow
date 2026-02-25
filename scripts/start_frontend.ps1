# ACE Veriflow — Start frontend (Next.js)
# Ensures .env.local exists with NEXT_PUBLIC_API_URL and runs npm run dev

$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
$frontend = Join-Path $root "frontend"
$envLocal = Join-Path $frontend ".env.local"

if (-not (Test-Path $envLocal)) {
    Set-Content -Path $envLocal -Value "NEXT_PUBLIC_API_URL=http://localhost:8000"
    Write-Host "Created frontend/.env.local with NEXT_PUBLIC_API_URL=http://localhost:8000"
}

Set-Location $frontend
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing npm dependencies..."
    npm install
}
Write-Host "Starting Next.js dev server..."
npm run dev
