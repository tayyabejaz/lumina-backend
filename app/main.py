"""FastAPI application entrypoint (fully async).

Run with multiple Uvicorn worker processes (uvicorn --workers N); scale horizontally behind
a load balancer. The app tier is stateless — all state lives in Supabase/Postgres, Redis, storage.

Kept import-light on purpose: this module does NOT import settings/DB at import time, so the
web process always boots and answers /health even before secrets/DB are configured.
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Adaptive Exam-Prep API", version="0.1.0")

# CORS — set CORS_ALLOW_ORIGINS to a comma-separated list of allowed origins
# (e.g. your Vercel domain). Defaults to "*" for first bring-up; lock this down for production.
_origins_env = os.getenv("CORS_ALLOW_ORIGINS", "*").strip()
if _origins_env == "*":
    _allow_origins, _allow_credentials = ["*"], False  # wildcard + credentials is invalid per CORS spec
else:
    _allow_origins = [o.strip() for o in _origins_env.split(",") if o.strip()]
    _allow_credentials = True

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allow_origins,
    allow_credentials=_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root() -> dict[str, str]:
    """Root route so the base URL responds (instead of 404). Useful for uptime checks."""
    return {"service": "adaptive-exam-prep-api", "status": "ok", "docs": "/docs", "health": "/health"}


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


# Routers are included per module, keeping the HTTP edge thin (SOLID: SRP).
# from app.modules.practice.router import router as practice_router
# app.include_router(practice_router, prefix="/v1")
