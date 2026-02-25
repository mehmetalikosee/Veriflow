"""
Deterministic verification: UL 60335-1 rules — 29.1/29.2 clearance & creepage, 8.1 accessibility, rated voltage, reinforced insulation.
"""
from app.schemas.extraction import BOMExtractionResult, BOMPart
from app.schemas.verification import VerificationFinding, VerificationResult, FindingStatus
from app.services.neo4j_service import get_clearance_min_mm, get_creepage_min_mm, get_requirement_by_id
from app.core.config import settings
import uuid


def _source_ref(requirement: dict, clause_ref: str) -> str:
    page = requirement.get("page_ref") or ""
    return f"UL 60335-1 Clause {clause_ref}" + (f" ({page})" if page else "")


def _req(rid: str, clause_ref: str, page_ref: str = "") -> dict:
    return {"id": rid, "clause_ref": clause_ref, "page_ref": page_ref}


async def verify_bom(submission_id: str, bom: BOMExtractionResult) -> VerificationResult:
    """
    UL 60335-1: 29.1 clearance, 29.2 creepage; 8.1 accessibility (IP); rated voltage; reinforced insulation (2×).
    """
    findings: list[VerificationFinding] = []
    confidence_threshold = settings.CONFIDENCE_THRESHOLD

    for i, part in enumerate(bom.parts):
        pd = getattr(part.pollution_degree, "value", part.pollution_degree) or 2
        ov = getattr(part.overvoltage_category, "value", part.overvoltage_category) or 2
        mg = getattr(part.material_group, "value", part.material_group) or "III"
        confidence = bom.extraction_confidence
        conf_review = confidence < confidence_threshold
        is_reinforced = part.insulation_type and str(part.insulation_type).lower() == "reinforced"

        # --- Clause 8.1 Accessibility: HV parts should have IP code ---
        if part.working_voltage_v is not None and part.working_voltage_v > 60:
            if not part.ip_code or not str(part.ip_code or "").strip().upper().startswith("IP"):
                req = _req("ul-60335-1-req-8-1-accessibility", "8.1", "Access to live parts")
                findings.append(VerificationFinding(
                    finding_id=str(uuid.uuid4()),
                    requirement_id=req["id"],
                    clause_ref=req["clause_ref"],
                    source_reference=_source_ref(req, req["clause_ref"]),
                    status=FindingStatus.MANUAL_REVIEW,
                    message=f"High-voltage part ({part.working_voltage_v} V) has no IP code; verify Clause 8 (accessibility to live parts).",
                    parameter_name="ip_code",
                    expected_value="IP code specified",
                    actual_value="none",
                    confidence=confidence,
                    requires_manual_review=True,
                ))

        # --- Rated voltage >= working voltage ---
        if part.rated_voltage_v is not None and part.working_voltage_v is not None:
            if part.rated_voltage_v < part.working_voltage_v:
                req = _req("ul-60335-1-req-rated-voltage", "7", "Rated voltage")
                findings.append(VerificationFinding(
                    finding_id=str(uuid.uuid4()),
                    requirement_id=req["id"],
                    clause_ref=req["clause_ref"],
                    source_reference=_source_ref(req, req["clause_ref"]),
                    status=FindingStatus.FAIL,
                    message=f"Rated voltage {part.rated_voltage_v} V is below working voltage {part.working_voltage_v} V (component underrated).",
                    parameter_name="rated_voltage_v",
                    expected_value=f">= {part.working_voltage_v}",
                    actual_value=str(part.rated_voltage_v),
                    confidence=confidence,
                    requires_manual_review=conf_review,
                ))

        # --- Clause 29.1 Clearance (2× for reinforced) ---
        if part.working_voltage_v is not None and part.clearance_mm is not None:
            min_clearance = await get_clearance_min_mm(part.working_voltage_v, pd, ov)
            req = _req("ul-60335-1-req-29-1-clearance", "29.1", "Table 29.1")
            if min_clearance is not None:
                required = 2.0 * min_clearance if is_reinforced else min_clearance
                passed = part.clearance_mm >= required
                finding = VerificationFinding(
                    finding_id=str(uuid.uuid4()),
                    requirement_id=req["id"],
                    clause_ref=req["clause_ref"],
                    source_reference=_source_ref(req, req["clause_ref"]),
                    status=FindingStatus.PASS if passed else FindingStatus.FAIL,
                    message=f"Clearance {part.clearance_mm} mm vs required min {required} mm (Clause 29.1{' reinforced 2×' if is_reinforced else ''})."
                    if passed else f"Clearance {part.clearance_mm} mm is below required {required} mm (Clause 29.1{' reinforced' if is_reinforced else ''}).",
                    parameter_name="clearance_mm",
                    expected_value=str(required),
                    actual_value=str(part.clearance_mm),
                    confidence=confidence,
                    requires_manual_review=conf_review,
                )
                if finding.requires_manual_review:
                    finding.status = FindingStatus.MANUAL_REVIEW
                findings.append(finding)

        # --- Clause 29.2 Creepage (2× for reinforced) ---
        if part.working_voltage_v is not None and part.creepage_distance_mm is not None:
            min_creepage = await get_creepage_min_mm(part.working_voltage_v, pd, mg)
            req = _req("ul-60335-1-req-29-2-creepage", "29.2", "Table 29.2")
            if min_creepage is not None:
                required = 2.0 * min_creepage if is_reinforced else min_creepage
                passed = part.creepage_distance_mm >= required
                finding = VerificationFinding(
                    finding_id=str(uuid.uuid4()),
                    requirement_id=req["id"],
                    clause_ref=req["clause_ref"],
                    source_reference=_source_ref(req, req["clause_ref"]),
                    status=FindingStatus.PASS if passed else FindingStatus.FAIL,
                    message=f"Creepage {part.creepage_distance_mm} mm vs required min {required} mm (Clause 29.2{' reinforced 2×' if is_reinforced else ''})."
                    if passed else f"Creepage {part.creepage_distance_mm} mm is below required {required} mm (Clause 29.2{' reinforced' if is_reinforced else ''}).",
                    parameter_name="creepage_distance_mm",
                    expected_value=str(required),
                    actual_value=str(part.creepage_distance_mm),
                    confidence=confidence,
                    requires_manual_review=conf_review,
                )
                if finding.requires_manual_review:
                    finding.status = FindingStatus.MANUAL_REVIEW
                findings.append(finding)

    # Overall status
    has_fail = any(f.status == FindingStatus.FAIL for f in findings)
    has_manual = any(f.requires_manual_review for f in findings)
    overall = "fail" if has_fail else ("manual_review" if has_manual else "pass")

    return VerificationResult(
        submission_id=submission_id,
        standard_id="ul-60335-1",
        findings=findings,
        overall_status=overall,
        summary=f"{len([f for f in findings if f.status == FindingStatus.PASS])} pass, "
                f"{len([f for f in findings if f.status == FindingStatus.FAIL])} fail, "
                f"{len([f for f in findings if f.requires_manual_review])} manual review.",
        rules_checked=["7", "8.1", "29.1", "29.2"],
    )
