# ACE Veriflow — Full E2E: Docker stack + Neo4j seed + backend + E2E test
# Requires: Docker Desktop, Python with backend deps (or venv)
# Optional: set $env:SKIP_DOCKER = "1" to skip bringing up containers (use existing Neo4j/Postgres)

$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
$backend = Join-Path $root "backend"
Set-Location $root

# 1. Start stack (unless SKIP_DOCKER)
if (-not $env:SKIP_DOCKER) {
    Write-Host "Starting Docker stack (Neo4j + Postgres)..."
    docker compose up -d
    # Wait for Neo4j HTTP
    $max = 30
    for ($i = 0; $i -lt $max; $i++) {
        try {
            $r = Invoke-WebRequest -Uri "http://localhost:7474" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
            break
        } catch {
            Start-Sleep -Seconds 2
            if ($i -eq $max - 1) { Write-Error "Neo4j did not become ready." }
        }
    }
    Write-Host "Neo4j is up."
    Start-Sleep -Seconds 3
    # Init Postgres audit table (idempotent; ignore errors if Postgres not ready)
    $sqlPath = Join-Path $backend "scripts\init_audit_db.sql"
    if (Test-Path $sqlPath) {
        try {
            Get-Content $sqlPath -Raw | docker compose exec -T postgres psql -U postgres -d veriflow 2>&1 | Out-Null
            Write-Host "Postgres audit schema applied."
        } catch {}
    }
}

# 2. Seed Neo4j
$env:NEO4J_PASSWORD = "veriflow123"
& (Join-Path $PSScriptRoot "seed_neo4j.ps1")
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

# 3. Ensure backend .env for local stack
$envPath = Join-Path $backend ".env"
$envContent = @"
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=veriflow123
DATABASE_URL=postgresql+asyncpg://postgres:veriflow@localhost:5432/veriflow
CORS_ORIGINS=["http://localhost:3000"]
CONFIDENCE_THRESHOLD=0.9
"@
if (-not (Test-Path $envPath)) {
    Set-Content -Path $envPath -Value $envContent
    Write-Host "Created backend/.env for local stack."
}

# 4. Start backend in background (if not already listening)
$health = "http://localhost:8000/health"
try {
    $null = Invoke-RestMethod -Uri $health -TimeoutSec 2
    Write-Host "Backend already running."
} catch {
    Write-Host "Starting backend..."
    $venvPython = Join-Path $backend ".venv\Scripts\python.exe"
    if (Test-Path $venvPython) {
        Start-Process -FilePath $venvPython -ArgumentList "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000" -WorkingDirectory $backend -WindowStyle Hidden
    } else {
        Start-Process -FilePath "python" -ArgumentList "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000" -WorkingDirectory $backend -WindowStyle Hidden
    }
    for ($i = 0; $i -lt 15; $i++) {
        Start-Sleep -Seconds 1
        try {
            $null = Invoke-RestMethod -Uri $health -TimeoutSec 2
            Write-Host "Backend is up."
            break
        } catch {}
        if ($i -eq 14) { Write-Error "Backend did not start." }
    }
}

# 5. Run E2E test
& (Join-Path $PSScriptRoot "run_e2e_test.ps1")
exit $LASTEXITCODE
