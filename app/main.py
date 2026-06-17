"""FastAPI application entrypoint (fully async).

Run with multiple Uvicorn worker processes (uvicorn --workers N); scale horizontally behind
a load balancer. The app tier is stateless — all state lives in Supabase/Postgres, Redis, storage.
"""
from fastapi import FastAPI

app = FastAPI(title="Adaptive Exam-Prep API", version="0.1.0")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


# Routers are included per module, keeping the HTTP edge thin (SOLID: SRP).
# from app.modules.practice.router import router as practice_router
# app.include_router(practice_router, prefix="/v1")
