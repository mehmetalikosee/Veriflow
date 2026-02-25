# Veriflow — ACE (Autonomous Compliance Engine)

A portfolio project: decision support for product compliance workflows. Maps product data to safety standards (e.g. IEC/UL 60335-1) via a knowledge graph; every finding is traceable to a specific clause (governance-first). Not affiliated with any certification body.

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 14 (App Router), Tailwind CSS, Shadcn/UI |
| Backend | Python FastAPI |
| Knowledge Graph | Neo4j (Standards → Requirements → Parameters) |
| Audit / Users | PostgreSQL |
| AI Orchestration | LangGraph (multi-step agentic workflows) |
| Models | GPT-4o / Claude 3.5 Sonnet |

## Quick Start

**Option A — One-command E2E (Docker + backend + test)**  
Requires Docker Desktop and Python/venv with backend deps.

```powershell
.\scripts\run_full_e2e.ps1
```

This brings up Neo4j + PostgreSQL (`docker compose up -d`), seeds Neo4j with the UL 60335-1 schema, starts the backend if needed, and runs the E2E test (1 pass + 1 fail with citations).

**Option B — Manual**

```powershell
# 1. Start stack
docker compose up -d
$env:NEO4J_PASSWORD = "veriflow123"
.\scripts\seed_neo4j.ps1

# 2. Backend (copy backend\.env.example to .env, set NEO4J_PASSWORD=veriflow123)
cd backend && .venv\Scripts\activate && uvicorn app.main:app --reload

# 3. Frontend
.\scripts\start_frontend.ps1
# Or: cd frontend && npm install && npm run dev
```

## Project Layout

```
Veriflow/
├── frontend/                 # Next.js 14 (App Router), Tailwind
│   ├── src/app/
│   │   ├── page.tsx          # Home
│   │   ├── upload/           # Upload BOM → extract → verify
│   │   └── dashboard/        # Side-by-side: document | findings + Approve/Reject
│   └── src/components/       # DocumentViewer, ApprovalPanel
├── backend/                  # FastAPI
│   ├── app/
│   │   ├── api/              # extraction, verification, audit, graph
│   │   ├── core/              # config
│   │   ├── schemas/           # Pydantic (BOM, VerificationFinding)
│   │   └── services/          # neo4j_service, verification_service
│   └── scripts/init_audit_db.sql
├── neo4j/
│   ├── schema/               # 01_schema.cypher, 02_ul_60335_nodes.cypher
│   └── seed/                 # 03_ul_60335_requirements.cypher, 04_ul_60335_tables.cypher
├── test-data/                # Real-life test
│   ├── bom_power_supply.csv       # 230 V; 1 pass, 1 fail (creepage gap)
│   └── bom_power_supply_compliant.csv
└── scripts/                  # run_tests.ps1, run_full_e2e.ps1, seed_neo4j.ps1, start_frontend.ps1
```

## Governance

- Every Fail/Warning includes `source_reference` (clause_id from graph).
- Results with confidence &lt; 90% are flagged for Manual Review.
- PostgreSQL audit log records who approved/rejected what and when.

## License

Portfolio / personal project. Not affiliated with UL or any certification body.
