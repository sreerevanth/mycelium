from fastapi import APIRouter
from .health import router as health_router
from .genomes import router as genomes_router
from .ws import router as ws_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(genomes_router)

__all__ = ["api_router", "ws_router"]
