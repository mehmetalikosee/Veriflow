"""Pydantic schema validation."""
import pytest
from pydantic import ValidationError
from app.schemas.extraction import BOMPart, BOMExtractionResult, MaterialGroup, PollutionDegree
from app.schemas.verification import VerificationFinding, VerificationResult, FindingStatus


class TestBOMPart:
    def test_minimal_valid(self):
        p = BOMPart(part_number="P1", quantity=1)
        assert p.part_number == "P1"
        assert p.quantity == 1
        assert p.working_voltage_v is None

    def test_full_valid(self):
        p = BOMPart(
            part_number="P1",
            quantity=2,
            working_voltage_v=230.0,
            clearance_mm=2.5,
            creepage_distance_mm=3.0,
            material_group=MaterialGroup.III,
            pollution_degree=PollutionDegree.TWO,
            ip_code="IP20",
        )
        assert p.clearance_mm == 2.5
        assert p.ip_code == "IP20"

    def test_quantity_ge_1(self):
        with pytest.raises(ValidationError):
            BOMPart(part_number="P1", quantity=0)

    def test_ip_code_pattern(self):
        BOMPart(part_number="P1", quantity=1, ip_code="IP54")
        with pytest.raises(ValidationError):
            BOMPart(part_number="P1", quantity=1, ip_code="IP5")  # need 2 digits


class TestVerificationFinding:
    def test_valid_finding(self):
        f = VerificationFinding(
            finding_id="f1",
            requirement_id="ul-60335-1-req-29-1-clearance",
            clause_ref="29.1",
            source_reference="UL 60335-1 Clause 29.1",
            status=FindingStatus.PASS,
            message="Clearance OK",
            confidence=0.95,
        )
        assert f.status == FindingStatus.PASS
        assert f.requires_manual_review is False

    def test_confidence_bounds(self):
        with pytest.raises(ValidationError):
            VerificationFinding(
                finding_id="f1",
                requirement_id="r1",
                clause_ref="29.1",
                source_reference="ref",
                status=FindingStatus.PASS,
                message="m",
                confidence=1.5,
            )


class TestVerificationResult:
    def test_overall_status_values(self):
        r = VerificationResult(
            submission_id="s1",
            overall_status="pass",
            findings=[],
        )
        assert r.overall_status == "pass"
        r2 = VerificationResult(submission_id="s2", overall_status="fail", findings=[])
        assert r2.overall_status == "fail"
        r3 = VerificationResult(submission_id="s3", overall_status="manual_review", findings=[])
        assert r3.overall_status == "manual_review"

    def test_invalid_overall_status(self):
        with pytest.raises(ValidationError):
            VerificationResult(
                submission_id="s1",
                overall_status="invalid",
                findings=[],
            )
