"""Goal Tactics – FastAPI application entry-point."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.routes import api_router
from app.schemas.common import err


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown hooks."""
    # Import here to avoid import-time side-effects in tests
    from app.services.scheduler import setup_scheduler

    setup_scheduler()
    yield


app = FastAPI(
    title="Goal Tactics API",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(api_router, prefix="/api")


# ── Global exception handler ────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content=err("INTERNAL_ERROR", str(exc)),
    )


@app.get("/health")
async def health():
    return {"status": "ok"}
