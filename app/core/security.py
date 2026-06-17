"""Auth: verify Supabase-issued JWTs (Supabase Auth, ADR-007 revision).

Returns the authenticated actor; authorization (RBAC+ReBAC) is enforced separately.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Actor:
    id: str
    role: str  # student | parent | tutor | teacher | admin


async def current_actor() -> Actor:
    """FastAPI dependency: decode + validate the Supabase JWT, load role. (stub)"""
    raise NotImplementedError
