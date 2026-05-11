# mycelium/backend/app/db/session.py

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class Base(DeclarativeBase):
    """SQLAlchemy declarative base for all MYCELIUM models."""
    pass


def create_engine() -> AsyncEngine:
    kwargs = dict(
        echo=settings.db_echo,
        pool_pre_ping=True,
    )
    if settings.is_development:
        # Use NullPool in dev to avoid connection leaks across reloads
        kwargs["poolclass"] = NullPool
    else:
        kwargs.update(
            pool_size=settings.db_pool_size,
            max_overflow=settings.db_max_overflow,
            pool_timeout=settings.db_pool_timeout,
            pool_recycle=3600,
        )

    return create_async_engine(settings.database_url, **kwargs)


engine: AsyncEngine = create_engine()

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency: yields an async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def get_db_context() -> AsyncGenerator[AsyncSession, None]:
    """Context manager for use outside FastAPI dependency injection."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Create all tables. Used in development; production uses Alembic."""
    from app.models import (  # noqa: F401 - import all models to register them
        genome,
        species,
        evolution_cycle,
        benchmark_result,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("database.initialized", tables=list(Base.metadata.tables.keys()))


async def dispose_engine() -> None:
    await engine.dispose()
    logger.info("database.engine.disposed")
