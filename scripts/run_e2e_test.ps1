# ACE Veriflow — E2E test (real-life BOM)
# Prereqs: Neo4j running with schema+seed loaded; backend running on port 8000.
# Compatible with PowerShell 5.1 (no -Form).

$ErrorActionPreference = "Stop"
$base = "http://localhost:8000"
$bomPath = Join-Path $PSScriptRoot "..\test-data\bom_power_supply.csv"

if (-not (Test-Path $bomPath)) {
    Write-Error "Test BOM not found: $bomPath"
    exit 1
}

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

Write-Host "1. Upload BOM and extract..."
$upload = Invoke-UploadBom -FilePath $bomPath
$ext = $upload.Object
Write-Host "   Parts extracted: $($ext.parts.Count)"

Write-Host "2. Run verification..."
$ver = Invoke-RestMethod -Uri "$base/api/verification/run" -Method Post -Body $upload.Content -ContentType "application/json"
Write-Host "   Overall status: $($ver.overall_status)"
Write-Host "   Summary: $($ver.summary)"

$failCount = ($ver.findings | Where-Object { $_.status -eq "fail" }).Count
$passCount = ($ver.findings | Where-Object { $_.status -eq "pass" }).Count
Write-Host "   Pass: $passCount, Fail: $failCount"

# Expected: 1 pass (29.1 clearance), 1 fail (29.2 creepage)
if ($failCount -eq 1 -and $passCount -eq 1) {
    Write-Host "PASS: Expected one pass and one fail (creepage gap)."
} else {
    Write-Host "Check: Expected 1 pass and 1 fail for bom_power_supply.csv."
}

Write-Host "3. Findings with source_reference:"
$ver.findings | ForEach-Object { Write-Host "   [$($_.clause_ref)] $($_.message) | $($_.source_reference)" }
