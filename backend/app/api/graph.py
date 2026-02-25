"""
Graph API: list requirements for auditor / agent.
"""
from fastapi import APIRouter
from app.services.neo4j_service import list_requirements_for_standard, get_requirement_by_id

router = APIRouter()


@router.get("/requirements")
async def list_requirements(standard_id: str = "ul-60335-1"):
    """List all requirements for a standard (UL 60335-1)."""
    return await list_requirements_for_standard(standard_id)


@router.get("/requirements/{requirement_id}")
async def get_requirement(requirement_id: str):
    """Get one requirement with parameters (for citation display)."""
    r = await get_requirement_by_id(requirement_id)
    if not r:
        return {"detail": "Not found"}
    return r
