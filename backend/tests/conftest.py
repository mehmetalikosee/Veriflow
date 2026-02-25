"""Pytest fixtures and Neo4j mocks for verification tests."""
import pytest
from unittest.mock import AsyncMock, patch
from app.schemas.extraction import BOMExtractionResult, BOMPart, MaterialGroup, PollutionDegree, OvervoltageCategory


@pytest.fixture
def sample_bom_pass_fail():
    """BOM that yields 1 pass (clearance) and 1 fail (creepage) for 230V."""
    return BOMExtractionResult(
        source_file="test.csv",
        parts=[
            BOMPart(
                part_number="PSU-230",
                description="230V isolation",
                quantity=1,
                working_voltage_v=230.0,
                clearance_mm=2.0,   # >= 1.5 required -> pass
                creepage_distance_mm=2.0,  # < 2.5 required -> fail
                material_group=MaterialGroup.III,
                pollution_degree=PollutionDegree.TWO,
                overvoltage_category=OvervoltageCategory.II,
                ip_code="IP20",
            ),
        ],
        extraction_confidence=0.92,
        warnings=[],
    )


@pytest.fixture
def sample_bom_all_pass():
    """BOM that passes both clearance and creepage."""
    return BOMExtractionResult(
        source_file="test.csv",
        parts=[
            BOMPart(
                part_number="PSU-230",
                quantity=1,
                working_voltage_v=230.0,
                clearance_mm=2.0,
                creepage_distance_mm=2.5,
                material_group=MaterialGroup.III,
                pollution_degree=PollutionDegree.TWO,
                overvoltage_category=OvervoltageCategory.II,
                ip_code="IP20",
            ),
        ],
        extraction_confidence=0.95,
        warnings=[],
    )


@pytest.fixture
def mock_neo4j():
    """Patch Neo4j service to return table values without a real DB."""
    req_29_1 = {
        "id": "ul-60335-1-req-29-1-clearance",
        "clause_ref": "29.1",
        "description": "Clearance",
        "rule_type": "min",
        "source_text": "Clearances shall be not less than those specified in Table 29.1.",
        "page_ref": "Table 29.1",
        "confidence_required": 0.9,
    }
    req_29_2 = {
        "id": "ul-60335-1-req-29-2-creepage",
        "clause_ref": "29.2",
        "description": "Creepage",
        "rule_type": "min",
        "source_text": "Creepage distances shall be not less than those specified in Table 29.2.",
        "page_ref": "Table 29.2",
        "confidence_required": 0.9,
    }

    async def get_clearance(voltage, pd, ov):
        if voltage <= 300 and pd == 2 and ov == 2:
            return 1.5
        return 2.0

    async def get_creepage(voltage, pd, mg):
        if voltage <= 250 and pd == 2 and mg == "III":
            return 2.5
        return 3.0

    async def get_req(rid):
        if "29-1" in rid:
            return req_29_1
        if "29-2" in rid:
            return req_29_2
        return None

    with patch("app.services.verification_service.get_clearance_min_mm", side_effect=get_clearance), \
         patch("app.services.verification_service.get_creepage_min_mm", side_effect=get_creepage), \
         patch("app.services.verification_service.get_requirement_by_id", side_effect=get_req):
        yield
