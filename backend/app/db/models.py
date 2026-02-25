"""SQLAlchemy models for audit log."""
from sqlalchemy import Column, BigInteger, Text, DateTime
from sqlalchemy.sql import func
from app.db.session import Base


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    finding_id = Column(Text, nullable=False, index=True)
    action = Column(Text, nullable=False)  # 'approve' | 'reject'
    user_id = Column(Text, nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
