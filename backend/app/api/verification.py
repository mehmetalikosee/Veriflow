"""
Verification endpoint: run deterministic checks against graph; return findings with source_reference.
"""
from fastapi import APIRouter, Query
from app.schemas.extraction import BOMExtractionResult
from app.schemas.verification import VerificationResult
from app.services.verification_service import verify_bom
import uuid

router = APIRouter()


@router.post("/run", response_model=VerificationResult)
async def run_verification(
    bom: BOMExtractionResult,
    use_workflow: bool = Query(False, description="Run via LangGraph workflow (fetch_requirements -> verify)"),
):
    """
    Run verification for extracted BOM. Every finding includes clause_id and source_reference.
    Results with confidence < 90% are flagged for manual review.
    Set use_workflow=true to run through the LangGraph verification graph.
    """
    submission_id = str(uuid.uuid4())
    if use_workflow:
        from app.workflows.verification_graph import run_verification_workflow
        return await run_verification_workflow(submission_id, bom)
    return await verify_bom(submission_id, bom)
