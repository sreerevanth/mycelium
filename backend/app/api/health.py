# mycelium/backend/app/api/health.py

import time
from typing import Any, Dict

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.db import get_db
from app.core.redis import get_redis
from app.core.config import settings

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/")
async def health_check() -> Dict[str, Any]:
    return {
        "status": "alive",
        "service": "mycelium-backend",
        "version": "0.1.0",
        "environment": settings.environment,
        "timestamp": time.time(),
    }


@router.get("/ready")
async def readiness_check(
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Checks database and redis connectivity."""
    checks: Dict[str, Any] = {}

    # Database check
    try:
        await db.execute(text("SELECT 1"))
        checks["database"] = {"status": "ok"}
    except Exception as e:
        checks["database"] = {"status": "error", "detail": str(e)}

    # Redis check
    try:
        redis = await get_redis()
        await redis.ping()
        checks["redis"] = {"status": "ok"}
    except Exception as e:
        checks["redis"] = {"status": "error", "detail": str(e)}

    overall = "ready" if all(v["status"] == "ok" for v in checks.values()) else "degraded"

    return {
        "status": overall,
        "checks": checks,
        "timestamp": time.time(),
    }


@router.get("/live")
async def liveness_check() -> Dict[str, str]:
    return {"status": "alive"}
