# Backend container (FastAPI, async), built with uv. Used by Railway for web + worker services.
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Install dependencies first (cached layer). uv.lock gives reproducible installs;
# --no-dev skips the dev group, --no-install-project defers installing our own code.
COPY pyproject.toml uv.lock* ./
RUN uv sync --no-dev --no-install-project

# Now copy the source and finish the install
COPY . .
RUN uv sync --no-dev

EXPOSE 8000

# Default (web) command — Uvicorn with multiple worker processes (async ASGI).
# Railway provides $PORT; the worker service overrides this command
# with: arq app.workers.worker.WorkerSettings  (see railway.toml).
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers ${WEB_CONCURRENCY:-2}"]
