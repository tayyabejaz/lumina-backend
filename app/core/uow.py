"""Unit of Work — wraps a use-case in one ACID transaction (atomic, consistent, isolated, durable).

Services depend on the UoW abstraction, not on SQLAlchemy directly (SOLID: DIP).
"""
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession


@asynccontextmanager
async def unit_of_work(session: AsyncSession):
    """Begin → commit on success → rollback on error. Guarantees atomicity."""
    try:
        async with session.begin():   # BEGIN ... COMMIT/ROLLBACK
            yield session
    except Exception:
        # session.begin() already rolled back; re-raise for the error handler.
        raise
