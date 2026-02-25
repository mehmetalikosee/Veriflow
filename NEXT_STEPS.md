# ACE Veriflow — Next steps and how to run tests

## Run all tests

### Backend (pytest)

From the project root:

```powershell
.\scripts\run_tests.ps1
```

Or manually:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt -r requirements-dev.txt
python -m pytest tests -v --tb=short
```

**Tests included:**

- **test_schemas.py** — Pydantic: BOMPart, BOMExtractionResult, VerificationFinding, VerificationResult
- **test_extraction.py** — CSV and Excel parsing (_parse_csv, _parse_excel)
- **test_verification_service.py** — verify_bom with mocked Neo4j (1 pass + 1 fail, all pass, manual_review)
- **test_api.py** — FastAPI: /health, /api/extraction/bom, /api/verification/run, /api/audit/log

### E2E (real Neo4j + backend)

**One command (Docker + seed + backend + test):**

```powershell
.\scripts\run_full_e2e.ps1
```

Requires Docker Desktop. This runs `docker compose up -d`, seeds Neo4j via `scripts/seed_neo4j.ps1`, applies Postgres audit schema, starts the backend if needed, then `run_e2e_test.ps1`.

**Manual:** Start **Neo4j** (e.g. `docker compose up -d`), then:

```powershell
$env:NEO4J_PASSWORD = "veriflow123"
.\scripts\seed_neo4j.ps1
```

Run Cypher in order if not using the script: `neo4j/schema/01_schema.cypher` → `02_ul_60335_nodes.cypher` → `seed/03_ul_60335_requirements.cypher` → `seed/04_ul_60335_tables.cypher`. Then start backend and run `.\scripts\run_e2e_test.ps1`. Expected: 1 pass (Clause 29.1), 1 fail (Clause 29.2), each with `source_reference`.

---

## What’s implemented

| Item | Status |
|------|--------|
| Neo4j schema + UL 60335-1 seed (clauses 8, 14, 29.1, 29.2 + tables) | Done |
| BOM extraction (CSV/Excel) + Pydantic schemas | Done |
| Deterministic verification (clearance, creepage) + source_reference | Done |
| Confidence &lt; 90% → manual review | Done |
| Auditor dashboard (side-by-side, Approve/Reject) | Done |
| Audit log API + **PostgreSQL persistence** (Phase 2) | Done |
| **LangGraph verification workflow** (Phase 1) | Done |
| Pytest unit + API tests (mocked Neo4j) | Done |
| E2E test script (real BOM) | Done |

---

## Next steps for you

1. **Run tests locally**  
   Use `.\scripts\run_tests.ps1` (or the manual pytest commands above). Fix any environment-specific failures (e.g. missing Python, venv path).

2. **PostgreSQL audit table**  
   If you want audit entries persisted, create the table (e.g. run `backend/scripts/init_audit_db.sql` on your Postgres DB) and set `DATABASE_URL` in `backend/.env`. The `/api/audit/log` endpoint will then set `persisted: true` when the insert succeeds.

3. **LangGraph workflow**  
   Use the same verification via the graph by calling:
   `POST /api/verification/run?use_workflow=true` with the same BOM JSON. The workflow runs: fetch_requirements → verify (existing logic).

4. **Extend the graph**  
   In `backend/app/workflows/verification_graph.py` you can add nodes (e.g. “extract_from_document” with an LLM) and more edges. The current graph is minimal so all logic stays in the existing verification service (deterministic, testable).

5. **PDF / drawings**  
   For multi-modal input (technical drawings), add an extraction path that calls a vision model and maps results into the same BOM/parameter schema, then run the same verification pipeline.

6. **More standards**  
   Add more Cypher seed files for other UL standards and extend `verification_service` (and optionally the graph) to select requirements by standard_id.

---

## Quick reference

| Action | Command / location |
|--------|--------------------|
| Backend tests | `.\scripts\run_tests.ps1` or `cd backend && pytest tests -v` |
| Full E2E (Docker + seed + backend + test) | `.\scripts\run_full_e2e.ps1` |
| E2E test only | `.\scripts\run_e2e_test.ps1` (Neo4j + backend running) |
| Seed Neo4j | `$env:NEO4J_PASSWORD='veriflow123'; .\scripts\seed_neo4j.ps1` |
| Start backend | `cd backend && uvicorn app.main:app --reload` |
| Start frontend | `.\scripts\start_frontend.ps1` or `cd frontend && npm run dev` |
| Start stack | `docker compose up -d` (Neo4j:7474/7687, Postgres:5432) |
| Init audit DB | Run `backend/scripts/init_audit_db.sql` on PostgreSQL (or run_full_e2e does it) |
