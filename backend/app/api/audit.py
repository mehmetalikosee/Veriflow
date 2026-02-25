"""
Audit trail: who approved/rejected what and when (PostgreSQL when configured).
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from app.db.audit_repo import log_audit_action as persist_audit, get_recent_audit_log

router = APIRouter()


class AuditAction(BaseModel):
    finding_id: str
    action: str  # "approve" | "reject"
    user_id: str
    comment: Optional[str] = None


@router.post("/log")
async def log_audit_action(action: AuditAction):
    """Log auditor decision. Persisted to PostgreSQL if DATABASE_URL is set."""
    if action.action not in ("approve", "reject"):
        return {"ok": False, "error": "action must be 'approve' or 'reject'"}
    persisted = await persist_audit(
        finding_id=action.finding_id,
        action=action.action,
        user_id=action.user_id,
        comment=action.comment,
    )
    return {
        "ok": True,
        "finding_id": action.finding_id,
        "action": action.action,
        "user_id": action.user_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "persisted": persisted,
    }


@router.get("/recent")
async def get_recent():
    """Return recent audit log entries (for demo; requires PostgreSQL)."""
    entries = await get_recent_audit_log(limit=50)
    return {"entries": entries}
