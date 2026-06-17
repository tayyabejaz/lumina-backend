"""Async Supabase/Postgres implementation of the repository Protocols (data-access layer).

Append-only inserts; reads can target the replica. Transactions are owned by the Unit of Work.
"""
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.practice.domain import Attempt


class SqlAttemptRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session  # injected per request

    async def add(self, attempt: Attempt) -> None:
        await self._s.execute(
            text(
                "INSERT INTO attempts (id, session_id, question_id, response, "
                "time_taken_ms, seq, answered_at) VALUES (:id, :sid, :qid, "
                "CAST(:resp AS jsonb), :ms, :seq, :ts)"
            ),
            {
                "id": attempt.id, "sid": attempt.session_id, "qid": attempt.question_id,
                "resp": attempt.response, "ms": attempt.time_taken_ms,
                "seq": attempt.seq, "ts": attempt.answered_at,
            },
        )

    async def next_question_id(self, session_id: str) -> str | None:
        # Delegates to the adaptive engine in practice; placeholder here.
        return None
