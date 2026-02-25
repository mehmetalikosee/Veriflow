# Veriflow (ACE) — Demo Guide for Engineers

This guide walks through running and demonstrating the **Veriflow — ACE (Autonomous Compliance Engine)** stack. It is a portfolio project; not affiliated with any certification body. BOM upload, deterministic verification against UL 60335-1 (clearance 29.1, creepage 29.2), and the auditor dashboard with Approve/Reject and audit trail.

---

## Prerequisites

- **Docker** (for Neo4j and optional PostgreSQL)
- **Python 3.11+** (backend)
- **Node.js 18+** (frontend)
- **PowerShell** (for seed and test scripts on Windows)

---

## 1. Start the Stack

### Option A: Full stack (Neo4j + PostgreSQL)

```powershell
cd c:\Users\memet\OneDrive\Desktop\Veriflow
docker compose up -d
```

- Neo4j: http://localhost:7474 (Bolt: 7687), auth: `neo4j` / `veriflow123`
- PostgreSQL: localhost:5432, user: `postgres`, password: `veriflow`, db: `veriflow`

Initialize the audit database (one-time):

```powershell
# From project root, with Postgres running:
docker compose exec -T postgres psql -U postgres -d veriflow -f - < backend/scripts/init_audit_db.sql
```

Or copy the contents of `backend/scripts/init_audit_db.sql` and run in any Postgres client connected to the `veriflow` database.

### Option B: Backend only (no Docker)

Backend works with **in-memory fallbacks** when Neo4j is not available: verification uses built-in tables (same values as seed). Audit log will not persist without PostgreSQL.

---

## 2. Seed Neo4j (UL 60335-1 schema and data)

Required only if you use Docker Neo4j and want graph-backed verification and citations:

```powershell
$env:NEO4J_PASSWORD = "veriflow123"
.\scripts\seed_neo4j.ps1
```

---

## 3. Start Backend and Frontend

**Backend:**

```powershell
cd backend
# Optional: copy .env.example to .env and set NEO4J_URI, NEO4J_PASSWORD, DATABASE_URL
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend** (new terminal):

```powershell
cd frontend
npm install
npm run dev
```

- Backend: http://localhost:8000 (API docs: http://localhost:8000/docs)
- Frontend: http://localhost:3000 (or 3001 if 3000 is in use)

---

## 4. Demo Flow for UL Engineer

### Step 1: Home

- Open **http://localhost:3000**
- Show **Veriflow — ACE** branding and navigation: Home, Upload & Verify, Auditor Dashboard.

### Step 2: Upload & Verify

- Go to **Upload & Verify**
- Use **Sample test data** (or drag & drop):
  - `test-data/bom_power_supply.csv` — expect **1 pass (29.1)**, **1 fail (29.2 creepage)**
  - `test-data/bom_power_supply_compliant.csv` — expect **all pass**
  - `test-data/bom_household_appliance.csv` — multiple parts, **all pass**
  - `test-data/bom_fail_both.csv` — **both clearance and creepage fail**
- After upload, run **Verify**; results are shown and stored for the dashboard.

### Step 3: Auditor Dashboard

- Go to **Auditor Dashboard**
- Show **document + findings** side-by-side
- For each finding: **Clause** (29.1 / 29.2), **Pass / Fail / Manual review**, **Source reference** (e.g. “UL 60335-1 Clause 29.1 (Table 29.1)”)
- Demonstrate **Approve** and **Reject**; these call `POST /api/audit/log` and are persisted if PostgreSQL is configured.

### Step 4: Audit Trail (optional)

- If PostgreSQL and `init_audit_db.sql` are in use, decisions are stored in `audit_log`
- **GET** http://localhost:8000/api/audit/recent — returns recent audit entries for demo

### Step 5: API Docs

- Open http://localhost:8000/docs
- Show **POST /api/extraction/bom** (upload BOM), **POST /api/verification/run** (run verification), **POST /api/audit/log** (log approve/reject), **GET /api/audit/recent**

---

## 5. Test Data and Expected Outcomes

| File | Expected overall | Pass | Fail | Notes |
|------|------------------|------|------|--------|
| `bom_power_supply.csv` | fail | 1 | 1 | Creepage below 2.5 mm |
| `bom_power_supply_compliant.csv` | pass | 2 | 0 | Meets 29.1 and 29.2 |
| `bom_household_appliance.csv` | pass | 4 | 0 | 2 parts × 2 findings each |
| `bom_fail_both.csv` | fail | 0 | 2 | Clearance and creepage both below |

---

## 6. Running Automated Tests

**Backend unit/integration tests:**

```powershell
cd backend
pytest
```

**Real-life BOM tests (backend must be running on port 8000):**

```powershell
.\scripts\run_real_life_tests.ps1
```

**Full E2E (Docker + seed + backend + E2E script):**

```powershell
.\scripts\run_full_e2e.ps1
```

---

## 7. Features Checklist for Demo

- [x] BOM upload (CSV/Excel), extraction with fallback column detection
- [x] Deterministic verification: Clause 29.1 (clearance), 29.2 (creepage) with **source_reference** citations
- [x] Neo4j-backed or in-memory fallback so verification always returns findings when BOM has voltage/clearance/creepage
- [x] Auditor dashboard: document viewer + findings list; Approve/Reject per finding
- [x] Audit log API: persist approve/reject to PostgreSQL when configured; GET /api/audit/recent for demo
- [x] Real-life test data and advanced test script (`run_real_life_tests.ps1`)
- [x] Professional frontend: branding, layout, status badges, sample test data list

---

## 8. Troubleshooting

- **CORS errors:** Backend allows origin 3000 and 3001; ensure frontend URL matches.
- **Neo4j connection:** Set `NEO4J_URI=bolt://localhost:7687` and `NEO4J_PASSWORD=veriflow123`; if Neo4j is down, verification still runs using in-memory tables.
- **No findings:** Ensure BOM has columns for working voltage and at least clearance or creepage (names or positions); see `backend/app/api/extraction.py` for supported headers.
- **Audit not persisting:** Set `DATABASE_URL` (e.g. `postgresql+asyncpg://postgres:veriflow@localhost:5432/veriflow`) and run `init_audit_db.sql` against the database.

---

*Veriflow — Ready for engineer demo.*
