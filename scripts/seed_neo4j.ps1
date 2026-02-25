# ACE Veriflow — Seed Neo4j with schema + UL 60335-1 data via HTTP API
# Prereq: Neo4j running (e.g. docker-compose up -d)
# Optional: $env:NEO4J_PASSWORD = "veriflow123" (default)

$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
$neo4jRoot = Join-Path $root "neo4j"
$neo4jHost = "localhost"
$port = 7474
$user = "neo4j"
$pass = if ($env:NEO4J_PASSWORD) { $env:NEO4J_PASSWORD } else { "veriflow123" }
$baseUrl = "http://${neo4jHost}:${port}"
$auth = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("${user}:${pass}"))

function Get-StatementsFromFile($path) {
    $text = Get-Content -Path $path -Raw
    # Remove // comment lines
    $lines = $text -split "`n"
    $cleaned = $lines | ForEach-Object {
        $line = $_.Trim()
        if ($line -match '^\s*//') { return "" }
        $line
    }
    $block = ($cleaned | Where-Object { $_ }) -join "`n"
    # Split by semicolon only when outside double-quoted strings (Cypher can have "text; more text" in literals)
    $statements = @()
    $sb = [System.Text.StringBuilder]::new()
    $inString = $false
    $i = 0
    $len = $block.Length
    while ($i -lt $len) {
        $c = $block[$i]
        if ($c -eq [char]92 -and $inString -and ($i + 1) -lt $len -and $block[$i + 1] -eq [char]34) {
            [void]$sb.Append($c)
            [void]$sb.Append($block[$i + 1])
            $i += 2
            continue
        }
        if ($c -eq [char]34) {
            $inString = -not $inString
            [void]$sb.Append($c)
        } elseif ($c -eq [char]59 -and -not $inString) {
            $stmt = $sb.ToString().Trim()
            if ($stmt.Length -gt 0) { $statements += $stmt }
            [void]$sb.Clear()
        } else {
            [void]$sb.Append($c)
        }
        $i++
    }
    $stmt = $sb.ToString().Trim()
    if ($stmt.Length -gt 0) { $statements += $stmt }
    $statements
}

function Escape-JsonString($s) {
    if (-not $s) { return "" }
    $sb = [System.Text.StringBuilder]::new()
    foreach ($c in $s.ToCharArray()) {
        if ($c -eq [char]92) { [void]$sb.Append('\\') }      # backslash
        elseif ($c -eq [char]34) { [void]$sb.Append('\"') } # double quote
        elseif ($c -eq [char]10) { [void]$sb.Append('\n') }   # LF
        elseif ($c -eq [char]13) { [void]$sb.Append('\r') }  # CR
        elseif ($c -eq [char]9) { [void]$sb.Append('\t') }   # tab
        else { [void]$sb.Append($c) }
    }
    $sb.ToString()
}

function Invoke-Neo4jStatement($statement) {
    $escaped = Escape-JsonString $statement
    $body = '{"statements":[{"statement":"' + $escaped + '"}]}'
    $headers = @{
        "Accept"        = "application/json;charset=UTF-8"
        "Content-Type"  = "application/json; charset=utf-8"
        "Authorization" = "Basic $auth"
    }
    $bodyBytes = [System.Text.Encoding]::UTF8.GetBytes($body)
    try {
        $create = Invoke-RestMethod -Uri "$baseUrl/db/neo4j/tx" -Method Post -Headers $headers -Body $bodyBytes
    } catch {
        Write-Error "Neo4j request failed: $_"
        return $false
    }
    if ($create.errors -and $create.errors.Count -gt 0) {
        Write-Error "Neo4j error: $($create.errors | ConvertTo-Json -Depth 5)"
        return $false
    }
    $commitUrl = $create.commit
    if (-not $commitUrl) {
        Write-Error "No commit URL in response"
        return $false
    }
    Invoke-RestMethod -Uri $commitUrl -Method Post -Headers $headers -Body '{}' | Out-Null
    return $true
}

$files = @(
    (Join-Path $neo4jRoot "schema\01_schema.cypher"),
    (Join-Path $neo4jRoot "schema\02_ul_60335_nodes.cypher"),
    (Join-Path $neo4jRoot "seed\03_ul_60335_requirements.cypher"),
    (Join-Path $neo4jRoot "seed\04_ul_60335_tables.cypher"),
    (Join-Path $neo4jRoot "seed\05_ul_60335_extra_requirements.cypher")
)

Write-Host "Neo4j seed: $baseUrl (user: $user)"
foreach ($f in $files) {
    if (-not (Test-Path $f)) {
        Write-Warning "Skip (not found): $f"
        continue
    }
    $name = Split-Path $f -Leaf
    $statements = Get-StatementsFromFile $f
    Write-Host "  $name -> $($statements.Count) statements"
    foreach ($s in $statements) {
        $ok = Invoke-Neo4jStatement $s
        if (-not $ok) {
            Write-Error "Failed executing: $($s.Substring(0, [Math]::Min(80, $s.Length)))..."
            exit 1
        }
    }
}
Write-Host "Neo4j seed done."
