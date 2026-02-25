# ACE Veriflow — Real-life test suite
# Runs all test-data BOMs against the backend and validates expected pass/fail.
# Prereq: Backend running on port 8000 (Neo4j optional; fallbacks used if graph empty).
# Compatible with PowerShell 5.1 (no -Form).

$ErrorActionPreference = "Stop"
$base = "http://localhost:8000"
$root = Split-Path $PSScriptRoot -Parent
$testData = Join-Path $root "test-data"

function Invoke-UploadBom {
    param([string]$FilePath)
    $uri = "$base/api/extraction/bom"
    $boundary = [System.Guid]::NewGuid().ToString("N")
    $fileName = [System.IO.Path]::GetFileName($FilePath)
    $fileBytes = [System.IO.File]::ReadAllBytes($FilePath)
    $enc = [System.Text.Encoding]::UTF8
    $crlf = "`r`n"
    $header = $enc.GetBytes(
        "--$boundary$crlf" +
        "Content-Disposition: form-data; name=`"file`"; filename=`"$fileName`"$crlf" +
        "Content-Type: text/csv$crlf$crlf"
    )
    $footer = $enc.GetBytes("$crlf--$boundary--$crlf")
    $body = New-Object byte[] ($header.Length + $fileBytes.Length + $footer.Length)
    [Array]::Copy($header, 0, $body, 0, $header.Length)
    [Array]::Copy($fileBytes, 0, $body, $header.Length, $fileBytes.Length)
    [Array]::Copy($footer, 0, $body, $header.Length + $fileBytes.Length, $footer.Length)
    $response = Invoke-WebRequest -Uri $uri -Method Post -ContentType "multipart/form-data; boundary=$boundary" -Body $body -UseBasicParsing
    @{ Content = $response.Content; Object = ($response.Content | ConvertFrom-Json) }
}

$tests = @(
    @{ File = "bom_power_supply.csv"; ExpectStatus = "fail"; ExpectPass = 1; ExpectFail = 1; Description = "230V PSU: 1 pass (29.1), 1 fail (29.2)" },
    @{ File = "bom_power_supply_compliant.csv"; ExpectStatus = "pass"; ExpectPass = 2; ExpectFail = 0; Description = "230V PSU compliant: all pass" },
    @{ File = "bom_household_appliance.csv"; ExpectStatus = "pass"; ExpectPass = 4; ExpectFail = 0; Description = "Household appliance: all pass" },
    @{ File = "bom_fail_both.csv"; ExpectStatus = "fail"; ExpectPass = 0; ExpectFail = 2; Description = "Both clearance and creepage fail" },
    @{ File = "bom_21_rated_voltage_fail.csv"; ExpectStatus = "fail"; ExpectPass = 2; ExpectFail = 1; Description = "Clause 7: rated voltage below working" },
    @{ File = "bom_22_reinforced_insulation.csv"; ExpectStatus = "pass"; ExpectPass = 2; ExpectFail = 0; Description = "Reinforced insulation 2×: pass" },
    @{ File = "bom_23_clause8_no_ip.csv"; ExpectStatus = "manual_review"; ExpectPass = 2; ExpectFail = 0; Description = "Clause 8.1: HV part no IP → manual review" },
    @{ File = "bom_24_reinforced_fail.csv"; ExpectStatus = "fail"; ExpectPass = 0; ExpectFail = 2; Description = "Reinforced but basic spacing: fail" }
)

$passed = 0
$failed = 0

foreach ($t in $tests) {
    $path = Join-Path $testData $t.File
    if (-not (Test-Path $path)) {
        Write-Host "SKIP: $($t.File) not found" -ForegroundColor Yellow
        continue
    }
    Write-Host ""
    Write-Host "--- $($t.File): $($t.Description) ---"
    try {
        $upload = Invoke-UploadBom -FilePath $path
        $ver = Invoke-RestMethod -Uri "$base/api/verification/run" -Method Post -Body $upload.Content -ContentType "application/json"
        $findings = @($ver.findings)
        $passCount = [int](@($findings | Where-Object { $_.status -eq "pass" }).Count)
        $failCount = [int](@($findings | Where-Object { $_.status -eq "fail" }).Count)
        $manualCount = [int](@($findings | Where-Object { $_.status -eq "manual_review" }).Count)
        $ok = ($ver.overall_status -eq $t.ExpectStatus) -and ($passCount -eq $t.ExpectPass) -and ($failCount -eq $t.ExpectFail)
        if ($ok) {
            Write-Host "  PASS: status=$($ver.overall_status), pass=$passCount, fail=$failCount" -ForegroundColor Green
            $passed++
        } else {
            Write-Host "  FAIL: expected status=$($t.ExpectStatus) pass=$($t.ExpectPass) fail=$($t.ExpectFail); got status=$($ver.overall_status) pass=$passCount fail=$failCount" -ForegroundColor Red
            $failed++
        }
        foreach ($f in $ver.findings) {
            if (-not $f.source_reference) {
                Write-Host "  WARN: finding missing source_reference" -ForegroundColor Yellow
            }
        }
    } catch {
        Write-Host "  ERROR: $_" -ForegroundColor Red
        $failed++
    }
}

Write-Host ""
Write-Host "Result: $passed passed, $failed failed"
if ($failed -gt 0) { exit 1 }
