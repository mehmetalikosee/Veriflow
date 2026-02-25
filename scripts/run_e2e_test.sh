#!/usr/bin/env bash
# ACE Veriflow — E2E test (real-life BOM)
# Prereqs: Neo4j running with schema+seed loaded; backend on port 8000.

set -e
BASE="http://localhost:8000"
BOM_PATH="$(dirname "$0")/../test-data/bom_power_supply.csv"

if [ ! -f "$BOM_PATH" ]; then
  echo "Test BOM not found: $BOM_PATH"
  exit 1
fi

echo "1. Upload BOM and extract..."
BOM_JSON=$(curl -s -X POST -F "file=@$BOM_PATH" "$BASE/api/extraction/bom")
echo "$BOM_JSON" | head -c 200
echo "..."

echo "2. Run verification..."
VER_JSON=$(curl -s -X POST -H "Content-Type: application/json" -d "$BOM_JSON" "$BASE/api/verification/run")
STATUS=$(echo "$VER_JSON" | grep -o '"overall_status":"[^"]*"' | cut -d'"' -f4)
echo "   Overall status: $STATUS"

echo "3. Findings with source_reference:"
echo "$VER_JSON" | grep -o '"source_reference":"[^"]*"' || true

echo "Done. Expected: 1 pass (29.1), 1 fail (29.2 creepage)."
