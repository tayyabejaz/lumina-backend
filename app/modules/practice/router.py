"""HTTP edge for Practice (thin). Wires dependencies and the Unit of Work; no business logic."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_session
from app.core.uow import unit_of_work
from app.core.security import Actor, current_actor
from app.modules.practice.repository import SqlAttemptRepository
from app.modules.practice.service import PracticeService
from app.modules.practice.schemas import SubmitAttemptIn, AttemptOut

router = APIRouter(tags=["practice"])


@router.post("/attempts", response_model=AttemptOut)
async def submit_attempt(
    body: SubmitAttemptIn,
    actor: Actor = Depends(current_actor),
    session: AsyncSession = Depends(get_session),
) -> AttemptOut:
    # from app.modules.marking.deterministic import DeterministicMarker
    async with unit_of_work(session):                 # one ACID transaction
        service = PracticeService(SqlAttemptRepository(session), marker=...)  # inject marker
        return await service.submit(body, seq=0)
