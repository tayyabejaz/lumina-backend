"""Pure domain entities for the Practice module — no framework or DB imports (SOLID: SRP)."""
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Attempt:
    id: str
    session_id: str
    question_id: str
    response: dict
    time_taken_ms: int
    seq: int
    answered_at: datetime
