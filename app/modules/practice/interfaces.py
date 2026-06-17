"""Abstractions the service depends on (SOLID: Dependency Inversion + Interface Segregation).

Concrete repositories implement these Protocols; services never import the implementations,
so storage (Supabase) can be swapped or mocked in tests without touching business logic.
"""
from typing import Protocol
from app.modules.practice.domain import Attempt


class AttemptRepository(Protocol):
    async def add(self, attempt: Attempt) -> None: ...
    async def next_question_id(self, session_id: str) -> str | None: ...


class Marker(Protocol):
    async def mark(self, question_id: str, response: dict) -> tuple[int, int, list[dict]]: ...
