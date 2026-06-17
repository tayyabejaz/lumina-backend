"""Async database engine + session (SQLAlchemy 2.0 async + asyncpg).

Scaling notes (100K req/s target):
- Connect via the Supabase pooler (Supavisor, transaction mode) so tens of thousands of
  client connections multiplex onto a small Postgres pool.
- Writes go to the primary engine; heavy reads use the read-replica engine.
- Every request gets a short-lived AsyncSession; transactions are explicit for ACID.
"""
from collections.abc import AsyncIterator
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from app.core.config import settings

engine = create_async_engine(
    settings.database_url, pool_size=20, max_overflow=10, pool_pre_ping=True
)
replica_engine = create_async_engine(
    settings.database_replica_url or settings.database_url, pool_size=20, max_overflow=10
)

SessionLocal = async_sessionmaker(engine, expire_on_commit=False)
ReplicaSession = async_sessionmaker(replica_engine, expire_on_commit=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency: one session per request (writes)."""
    async with SessionLocal() as session:
        yield session


async def get_read_session() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency: replica session for read-only queries."""
    async with ReplicaSession() as session:
        yield session
