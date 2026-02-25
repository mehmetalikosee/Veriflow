"""
LangGraph verification workflow: fetch requirement from graph -> extract value from BOM -> compare.
Deterministic comparison; every step traceable for governance.
"""
from typing import TypedDict
from langgraph.graph import StateGraph, END

from app.schemas.extraction import BOMExtractionResult
from app.schemas.verification import VerificationResult
from app.services.verification_service import verify_bom


class VerificationState(TypedDict, total=False):
    """State for the verification graph."""
    submission_id: str
    bom: BOMExtractionResult
    requirement_ids: list
    findings: list
    result: VerificationResult


async def node_fetch_requirements(state: VerificationState) -> VerificationState:
    """Step 1: Resolve which requirements apply (e.g. from standard_id)."""
    # For UL 60335-1 we always check 29.1 and 29.2 when BOM has voltage/clearance/creepage
    ids = []
    for part in state["bom"].parts:
        if part.working_voltage_v is not None:
            if part.clearance_mm is not None:
                ids.append("ul-60335-1-req-29-1-clearance")
            if part.creepage_distance_mm is not None:
                ids.append("ul-60335-1-req-29-2-creepage")
    state["requirement_ids"] = list(dict.fromkeys(ids))  # dedupe
    return state


async def node_verify(state: VerificationState) -> VerificationState:
    """Step 2: Run deterministic verification (existing service)."""
    result = await verify_bom(state["submission_id"], state["bom"])
    state["result"] = result
    state["findings"] = result.findings
    return state


def build_verification_graph() -> StateGraph:
    """Build the graph: fetch_requirements -> verify -> end."""
    graph = StateGraph(VerificationState)
    graph.add_node("fetch_requirements", node_fetch_requirements)
    graph.add_node("verify", node_verify)
    graph.set_entry_point("fetch_requirements")
    graph.add_edge("fetch_requirements", "verify")
    graph.add_edge("verify", END)
    return graph


def get_verification_graph():
    """Compiled graph (singleton)."""
    g = build_verification_graph()
    return g.compile()


async def run_verification_workflow(submission_id: str, bom: BOMExtractionResult) -> VerificationResult:
    """Run the full workflow and return verification result."""
    graph = get_verification_graph()
    initial: VerificationState = {
        "submission_id": submission_id,
        "bom": bom,
        "requirement_ids": [],
        "findings": [],
        "result": None,
    }
    final = await graph.ainvoke(initial)
    assert final.get("result") is not None
    return final["result"]
