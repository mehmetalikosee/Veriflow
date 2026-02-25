# ACE Veriflow — Run all backend tests
# Usage: .\scripts\run_tests.ps1

$ErrorActionPreference = "Stop"
$backend = Join-Path $PSScriptRoot "..\backend"

Push-Location $backend
try {
    if (-not (Test-Path ".venv")) {
        Write-Host "Creating venv..."
        python -m venv .venv
    }
    & .\.venv\Scripts\Activate.ps1
    pip install -q -r requirements.txt -r requirements-dev.txt
    Write-Host "Running pytest..."
    python -m pytest tests -v --tb=short
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
} finally {
    Pop-Location
}
Write-Host "Tests done."
