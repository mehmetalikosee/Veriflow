"""Audit log repository: persist to PostgreSQL when available."""
from typing import Optional, List
from app.db.session import get_session
from app.db.models import AuditLog
from sqlalchemy import select, desc


async def get_recent_audit_log(limit: int = 50) -> List[dict]:
    """Return recent audit log entries for demo. Empty if no DB."""
    session = await get_session()
    if session is None:
        return []
    try:
        result = await session.execute(
            select(AuditLog).order_by(desc(AuditLog.created_at)).limit(limit)
        )
        rows = result.scalars().all()
        return [
            {
                "id": r.id,
                "finding_id": r.finding_id,
                "action": r.action,
                "user_id": r.user_id,
                "comment": r.comment,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in rows
        ]
    except Exception:
        return []
    finally:
        await session.close()


async def log_audit_action(finding_id: str, action: str, user_id: str, comment: Optional[str] = None) -> bool:
    """Returns True if persisted to DB, False if skipped (no DB or error)."""
    session = await get_session()
    if session is None:
        return False
    try:
        session.add(AuditLog(finding_id=finding_id, action=action, user_id=user_id, comment=comment))
        await session.commit()
        return True
    except Exception:
        await session.rollback()
        return False
    finally:
        await session.close()
