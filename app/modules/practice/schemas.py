"""Pydantic request/response DTOs (validation + OpenAPI contract). Mirrors web/mobile types."""
from pydantic import BaseModel


class SubmitAttemptIn(BaseModel):
    session_id: str
    question_id: str
    response: dict
    time_taken_ms: int


class MarkOut(BaseModel):
    criterion: str
    awarded: int
    max: int
    feedback: str | None = None


class AttemptOut(BaseModel):
    attempt_id: str
    marking: str  # "complete" | "queued"
    awarded: int
    max: int
    marks: list[MarkOut]
    next_url: str | None = None
