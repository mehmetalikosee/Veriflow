"""API endpoints with mocked Neo4j."""
import io
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

# Patch Neo4j before importing app (so verification uses mocks)
@pytest.fixture(autouse=True)
def mock_neo4j_for_api():
    async def get_clearance(*_): return 1.5
    async def get_creepage(*_): return 2.5
    req = {"id": "ul-60335-1-req-29-1-clearance", "clause_ref": "29.1", "page_ref": "Table 29.1"}
    async def get_req(rid):
        if "29-2" in rid:
            return {"id": "ul-60335-1-req-29-2-creepage", "clause_ref": "29.2", "page_ref": "Table 29.2"}
        return req
    with patch("app.services.verification_service.get_clearance_min_mm", side_effect=get_clearance), \
         patch("app.services.verification_service.get_creepage_min_mm", side_effect=get_creepage), \
         patch("app.services.verification_service.get_requirement_by_id", side_effect=get_req):
        yield


@pytest.fixture
def client():
    from app.main import app
    return TestClient(app)


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_extract_bom_csv(client):
    csv = b"part_number,description,quantity,working_voltage_v,clearance_mm,creepage_distance_mm\nPSU-230,Desc,1,230,2.0,2.5\n"
    r = client.post("/api/extraction/bom", files={"file": ("bom.csv", io.BytesIO(csv), "text/csv")})
    assert r.status_code == 200
    data = r.json()
    assert data["source_file"] == "bom.csv"
    assert len(data["parts"]) == 1
    assert data["parts"][0]["working_voltage_v"] == 230.0


def test_verification_run(client):
    bom_json = {
        "source_file": "test.csv",
        "parts": [
            {
                "part_number": "PSU-230",
                "quantity": 1,
                "working_voltage_v": 230.0,
                "clearance_mm": 2.0,
                "creepage_distance_mm": 2.0,
                "material_group": "III",
                "pollution_degree": 2,
                "overvoltage_category": 2,
            }
        ],
        "extraction_confidence": 0.92,
        "warnings": [],
    }
    r = client.post("/api/verification/run", json=bom_json)
    assert r.status_code == 200
    data = r.json()
    assert "findings" in data
    assert data["overall_status"] in ("pass", "fail", "manual_review")
    for f in data["findings"]:
        assert "source_reference" in f
        assert "clause_ref" in f


def test_audit_log(client):
    r = client.post(
        "/api/audit/log",
        json={"finding_id": "f1", "action": "approve", "user_id": "auditor-1"},
    )
    assert r.status_code == 200
    assert r.json()["ok"] is True
    assert r.json()["action"] == "approve"
