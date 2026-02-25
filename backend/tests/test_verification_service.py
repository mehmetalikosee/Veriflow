"""Verification service: deterministic comparison with mocked Neo4j."""
import pytest
from app.services.verification_service import verify_bom
from app.schemas.verification import FindingStatus


@pytest.mark.asyncio
async def test_verify_bom_one_pass_one_fail(sample_bom_pass_fail, mock_neo4j):
    result = await verify_bom("sub-1", sample_bom_pass_fail)
    assert result.submission_id == "sub-1"
    assert result.standard_id == "ul-60335-1"
    assert result.overall_status == "fail"
    pass_findings = [f for f in result.findings if f.status == FindingStatus.PASS]
    fail_findings = [f for f in result.findings if f.status == FindingStatus.FAIL]
    assert len(pass_findings) == 1
    assert len(fail_findings) == 1
    assert "29.1" in pass_findings[0].clause_ref
    assert "29.2" in fail_findings[0].clause_ref
    assert "2.5" in fail_findings[0].expected_value
    assert "2.0" in fail_findings[0].actual_value
    for f in result.findings:
        assert f.source_reference
        assert f.requirement_id


@pytest.mark.asyncio
async def test_verify_bom_all_pass(sample_bom_all_pass, mock_neo4j):
    result = await verify_bom("sub-2", sample_bom_all_pass)
    assert result.overall_status == "pass"
    assert all(f.status == FindingStatus.PASS for f in result.findings)
    assert "pass" in result.summary.lower()


@pytest.mark.asyncio
async def test_verify_bom_low_confidence_flagged(sample_bom_all_pass, mock_neo4j):
    sample_bom_all_pass.extraction_confidence = 0.85
    result = await verify_bom("sub-3", sample_bom_all_pass)
    assert result.overall_status == "manual_review"
    assert any(f.requires_manual_review for f in result.findings)
