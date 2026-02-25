"""Async PostgreSQL session (optional). If DATABASE_URL not set, audit falls back to in-memory."""
from typing import Optional
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings

Base = declarative_base()
_engine = None
_session_factory: Optional[async_sessionmaker[AsyncSession]] = None


def get_engine():
    global _engine
    if _engine is None and _is_postgres_configured():
        _engine = create_async_engine(
            settings.DATABASE_URL,
            echo=False,
        )
    return _engine


def _is_postgres_configured() -> bool:
    url = (settings.DATABASE_URL or "").strip()
    return "postgresql" in url


def get_session_factory() -> Optional[async_sessionmaker[AsyncSession]]:
    global _session_factory
    engine = get_engine()
    if engine is None:
        return None
    if _session_factory is None:
        _session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    return _session_factory


async def get_session() -> Optional[AsyncSession]:
    factory = get_session_factory()
    if factory is None:
        return None
    return factory()
