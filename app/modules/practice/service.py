"""Application use-cases for Practice (orchestration only — SOLID: SRP).

Depends on the AttemptRepository and Marker *abstractions* (DIP). The Unit of Work makes the
whole submit operation a single ACID transaction: the attempt and its marks commit together.
"""
import uuid
from datetime import datetime, timezone
from app.modules.practice.domain import Attempt
from app.modules.practice.interfaces import AttemptRepository, Marker
from app.modules.practice.schemas import SubmitAttemptIn, AttemptOut, MarkOut


class PracticeService:
    def __init__(self, attempts: AttemptRepository, marker: Marker) -> None:
        self._attempts = attempts
        self._marker = marker

    async def submit(self, data: SubmitAttemptIn, seq: int) -> AttemptOut:
        attempt = Attempt(
            id=str(uuid.uuid4()), session_id=data.session_id, question_id=data.question_id,
            response=data.response, time_taken_ms=data.time_taken_ms, seq=seq,
            answered_at=datetime.now(timezone.utc),
        )
        await self._attempts.add(attempt)
        awarded, total, marks = await self._marker.mark(data.question_id, data.response)
        return AttemptOut(
            attempt_id=attempt.id, marking="complete", awarded=awarded, max=total,
            marks=[MarkOut(**m) for m in marks],
            next_url=f"/v1/sessions/{data.session_id}/next",
        )
