"""Real-life BOM verification scenarios: multiple parts, pass/fail mix, citations."""
import pytest
from app.schemas.extraction import (
    BOMExtractionResult,
    BOMPart,
    MaterialGroup,
    PollutionDegree,
    OvervoltageCategory,
)
from app.services.verification_service import verify_bom
from app.schemas.verification import FindingStatus


@pytest.fixture
def mock_neo4j_real_life():
    """Neo4j fallback-style: 230V pd2 ov2 -> clearance 1.5, creepage 2.5."""
    from unittest.mock import patch, AsyncMock
    async def get_clearance(voltage, pd, ov):
        if voltage <= 300 and pd == 2 and ov == 2:
            return 1.5
        return 2.0
    async def get_creepage(voltage, pd, mg):
        if voltage <= 250 and pd == 2 and (mg == "III" or mg == 3):
            return 2.5
        return 3.0
    req_29_1 = {"id": "ul-60335-1-req-29-1-clearance", "clause_ref": "29.1", "page_ref": "Table 29.1"}
    req_29_2 = {"id": "ul-60335-1-req-29-2-creepage", "clause_ref": "29.2", "page_ref": "Table 29.2"}
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


@pytest.mark.asyncio
async def test_household_appliance_multiple_parts_all_pass(mock_neo4j_real_life):
    """Household appliance BOM: 2 parts with clearance+creepage -> 4 pass."""
    bom = BOMExtractionResult(
        source_file="bom_household_appliance.csv",
        parts=[
            BOMPart(
                part_number="MAINS-230",
                description="Mains input 230V AC",
                quantity=1,
                working_voltage_v=230.0,
                clearance_mm=2.5,
                creepage_distance_mm=3.0,
                material_group=MaterialGroup.III,
                pollution_degree=PollutionDegree.TWO,
                overvoltage_category=OvervoltageCategory.II,
                ip_code="IP20",
            ),
            BOMPart(
                part_number="ISOL-230",
                description="Isolation barrier 230V",
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
        extraction_confidence=0.92,
        warnings=[],
    )
    result = await verify_bom("sub-household", bom)
    assert result.overall_status == "pass"
    pass_count = len([f for f in result.findings if f.status == FindingStatus.PASS])
    fail_count = len([f for f in result.findings if f.status == FindingStatus.FAIL])
    assert pass_count == 4
    assert fail_count == 0
    for f in result.findings:
        assert f.source_reference and ("29.1" in f.source_reference or "29.2" in f.source_reference)


@pytest.mark.asyncio
async def test_fail_both_clearance_and_creepage(mock_neo4j_real_life):
    """One part below both limits -> 2 fail."""
    bom = BOMExtractionResult(
        source_file="bom_fail_both.csv",
        parts=[
            BOMPart(
                part_number="FAIL-230",
                working_voltage_v=230.0,
                clearance_mm=1.0,
                creepage_distance_mm=1.5,
                material_group=MaterialGroup.III,
                pollution_degree=PollutionDegree.TWO,
                overvoltage_category=OvervoltageCategory.II,
                quantity=1,
                ip_code="IP20",
            ),
        ],
        extraction_confidence=0.9,
        warnings=[],
    )
    result = await verify_bom("sub-fail-both", bom)
    assert result.overall_status == "fail"
    pass_count = len([f for f in result.findings if f.status == FindingStatus.PASS])
    fail_count = len([f for f in result.findings if f.status == FindingStatus.FAIL])
    assert pass_count == 0
    assert fail_count == 2
    clause_refs = {f.clause_ref for f in result.findings}
    assert "29.1" in clause_refs and "29.2" in clause_refs


@pytest.mark.asyncio
async def test_power_supply_one_pass_one_fail(mock_neo4j_real_life):
    """Classic PSU case: clearance pass, creepage fail."""
    bom = BOMExtractionResult(
        source_file="bom_power_supply.csv",
        parts=[
            BOMPart(
                part_number="PSU-230",
                working_voltage_v=230.0,
                clearance_mm=2.0,
                creepage_distance_mm=2.0,
                material_group=MaterialGroup.III,
                pollution_degree=PollutionDegree.TWO,
                overvoltage_category=OvervoltageCategory.II,
                quantity=1,
                ip_code="IP20",
            ),
        ],
        extraction_confidence=0.92,
        warnings=[],
    )
    result = await verify_bom("sub-psu", bom)
    assert result.overall_status == "fail"
    pass_count = len([f for f in result.findings if f.status == FindingStatus.PASS])
    fail_count = len([f for f in result.findings if f.status == FindingStatus.FAIL])
    assert pass_count == 1
    assert fail_count == 1
    fail_f = next(f for f in result.findings if f.status == FindingStatus.FAIL)
    assert "29.2" in fail_f.clause_ref
    assert "2.5" in fail_f.expected_value
    assert "2.0" in fail_f.actual_value


@pytest.mark.asyncio
async def test_rated_voltage_fail(mock_neo4j_real_life):
    """Clause 7: rated_voltage_v < working_voltage_v -> fail."""
    bom = BOMExtractionResult(
        source_file="bom_21_rated_voltage_fail.csv",
        parts=[
            BOMPart(
                part_number="UNDER-230",
                working_voltage_v=230.0,
                rated_voltage_v=200.0,
                clearance_mm=2.0,
                creepage_distance_mm=2.5,
                material_group=MaterialGroup.III,
                pollution_degree=PollutionDegree.TWO,
                overvoltage_category=OvervoltageCategory.II,
                quantity=1,
                ip_code="IP20",
            ),
        ],
        extraction_confidence=0.92,
        warnings=[],
    )
    result = await verify_bom("sub-rated-fail", bom)
    assert result.overall_status == "fail"
    fail_findings = [f for f in result.findings if f.status == FindingStatus.FAIL]
    assert len(fail_findings) >= 1
    clause7 = next((f for f in fail_findings if f.clause_ref == "7"), None)
    assert clause7 is not None
    assert "200" in clause7.actual_value and "230" in clause7.expected_value


@pytest.mark.asyncio
async def test_reinforced_insulation_pass(mock_neo4j_real_life):
    """Reinforced insulation: 2× min (3.0 / 5.0 mm) -> pass."""
    bom = BOMExtractionResult(
        source_file="bom_22_reinforced_insulation.csv",
        parts=[
            BOMPart(
                part_number="REIN-230",
                working_voltage_v=230.0,
                clearance_mm=3.0,
                creepage_distance_mm=5.0,
                material_group=MaterialGroup.III,
                pollution_degree=PollutionDegree.TWO,
                overvoltage_category=OvervoltageCategory.II,
                quantity=1,
                insulation_type="reinforced",
                ip_code="IP20",
            ),
        ],
        extraction_confidence=0.92,
        warnings=[],
    )
    result = await verify_bom("sub-rein-pass", bom)
    assert result.overall_status == "pass"
    pass_count = len([f for f in result.findings if f.status == FindingStatus.PASS])
    assert pass_count == 2


@pytest.mark.asyncio
async def test_reinforced_insulation_fail(mock_neo4j_real_life):
    """Reinforced but basic spacing -> 2 fail."""
    bom = BOMExtractionResult(
        source_file="bom_24_reinforced_fail.csv",
        parts=[
            BOMPart(
                part_number="REIN-FAIL",
                working_voltage_v=230.0,
                clearance_mm=2.0,
                creepage_distance_mm=2.5,
                material_group=MaterialGroup.III,
                pollution_degree=PollutionDegree.TWO,
                overvoltage_category=OvervoltageCategory.II,
                quantity=1,
                insulation_type="reinforced",
                ip_code="IP20",
            ),
        ],
        extraction_confidence=0.92,
        warnings=[],
    )
    result = await verify_bom("sub-rein-fail", bom)
    assert result.overall_status == "fail"
    fail_count = len([f for f in result.findings if f.status == FindingStatus.FAIL])
    assert fail_count == 2


@pytest.mark.asyncio
async def test_clause8_no_ip_manual_review(mock_neo4j_real_life):
    """HV part without ip_code -> Clause 8.1 manual_review."""
    bom = BOMExtractionResult(
        source_file="bom_23_clause8_no_ip.csv",
        parts=[
            BOMPart(
                part_number="NOIP-230",
                working_voltage_v=230.0,
                clearance_mm=2.0,
                creepage_distance_mm=2.5,
                material_group=MaterialGroup.III,
                pollution_degree=PollutionDegree.TWO,
                overvoltage_category=OvervoltageCategory.II,
                quantity=1,
                ip_code=None,
            ),
        ],
        extraction_confidence=0.92,
        warnings=[],
    )
    result = await verify_bom("sub-8.1", bom)
    assert result.overall_status == "manual_review"
    manual = [f for f in result.findings if f.status == FindingStatus.MANUAL_REVIEW]
    assert any(f.clause_ref == "8.1" for f in manual)
