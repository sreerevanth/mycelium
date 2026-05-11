# mycelium/backend/app/main.py

import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.core.redis import get_redis, close_redis
from app.db import init_db, dispose_engine
from app.api import api_router
from app.api.ws import router as ws_router

# Initialize logging before anything else
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan: startup → yield → shutdown."""
    logger.info(
        "mycelium.starting",
        environment=settings.environment,
        version="0.1.0",
    )

    # Initialize database (create tables if not using alembic in dev)
    if settings.is_development:
        await init_db()

    # Warm up Redis connection
    redis = await get_redis()
    await redis.ping()
    logger.info("mycelium.ready")

    yield  # ── application is running ──────────────────────────────────────────

    logger.info("mycelium.shutting_down")
    await close_redis()
    await dispose_engine()
    logger.info("mycelium.stopped")


def create_app() -> FastAPI:
    app = FastAPI(
        title="MYCELIUM Evolution Runtime",
        description="Autonomous evolutionary software runtime - API layer",
        version="0.1.0",
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
        lifespan=lifespan,
    )

    # ─── CORS ─────────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ─── REQUEST TIMING MIDDLEWARE ────────────────────────────────────────────
    @app.middleware("http")
    async def add_timing_header(request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000
        response.headers["X-Process-Time-Ms"] = f"{duration_ms:.2f}"
        return response

    # ─── GLOBAL EXCEPTION HANDLER ─────────────────────────────────────────────
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(
            "unhandled.exception",
            path=request.url.path,
            method=request.method,
            error=str(exc),
            exc_info=exc,
        )
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error", "type": type(exc).__name__},
        )

    # ─── ROUTERS ──────────────────────────────────────────────────────────────
    app.include_router(api_router, prefix="/api/v1")
    app.include_router(ws_router)  # WebSocket routes at /ws/*

    @app.get("/")
    async def root():
        return {
            "service": "MYCELIUM Evolution Runtime",
            "version": "0.1.0",
            "status": "operational",
            "docs": "/docs",
        }

    return app


app = create_app()
