"""
Verification findings with mandatory source reference (governance).
"""
from pydantic import BaseModel, Field
from typing import Optional, Literal
from enum import Enum


class FindingStatus(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"
    MANUAL_REVIEW = "manual_review"


class VerificationFinding(BaseModel):
    """Single finding: must reference clause_id from graph."""
    finding_id: str = Field(..., description="Unique id for this finding")
    requirement_id: str = Field(..., description="Neo4j Requirement.id (e.g. ul-60335-1-req-29-1-clearance)")
    clause_ref: str = Field(..., description="Human-readable clause e.g. 29.1")
    source_reference: str = Field(..., description="Citation: standard + clause + page_ref")
    status: FindingStatus
    message: str = Field(..., description="Short explanation")
    parameter_name: Optional[str] = None
    expected_value: Optional[str] = None  # From standard / table
    actual_value: Optional[str] = None    # From product data
    confidence: float = Field(ge=0, le=1)
    requires_manual_review: bool = Field(False, description="True if confidence < threshold")


class VerificationResult(BaseModel):
    """Full verification run for one product/submission."""
    submission_id: str
    standard_id: str = "ul-60335-1"
    findings: list[VerificationFinding] = Field(default_factory=list)
    overall_status: Literal["pass", "fail", "manual_review"] = "pass"
    summary: Optional[str] = None
    rules_checked: Optional[list[str]] = Field(
        default_factory=lambda: ["7", "8.1", "29.1", "29.2"],
        description="Clause IDs applied (rated voltage, accessibility, clearance, creepage)",
    )
