"""RBAC + ReBAC authorization (ADR-008). Pure policy function, injected as a dependency."""
from app.core.security import Actor


def authorize(actor: Actor, action: str, *, owner_student_id: str | None = None) -> bool:
    """Require BOTH a role capability AND an in-scope relationship link. Deny by default."""
    # return has_capability(actor.role, action) and in_scope(actor, owner_student_id)
    return False
