# mycelium/backend/app/core/config.py

from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ─── ENVIRONMENT ──────────────────────────────────────────────────────────
    environment: str = "development"
    log_level: str = "DEBUG"
    debug: bool = True

    # ─── SERVER ───────────────────────────────────────────────────────────────
    host: str = "0.0.0.0"
    port: int = 8000
    allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:80"]

    # ─── DATABASE ─────────────────────────────────────────────────────────────
    database_url: str = "postgresql+asyncpg://mycelium:mycelium_secret@postgres:5432/mycelium"
    database_sync_url: str = "postgresql://mycelium:mycelium_secret@postgres:5432/mycelium"
    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_pool_timeout: int = 30
    db_echo: bool = False

    # ─── REDIS ────────────────────────────────────────────────────────────────
    redis_url: str = "redis://redis:6379/0"
    redis_queue_url: str = "redis://redis:6379/1"
    redis_pubsub_url: str = "redis://redis:6379/2"
    redis_event_channel: str = "mycelium:events"

    # ─── SECURITY ─────────────────────────────────────────────────────────────
    secret_key: str = "dev-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440

    # ─── EVOLUTION ENGINE ─────────────────────────────────────────────────────
    mutation_rate: float = 0.15
    crossover_rate: float = 0.05
    extinction_threshold: float = 0.20
    elite_survival_ratio: float = 0.10
    max_population_size: int = 50
    evolution_cycle_interval_sec: int = 30
    min_benchmark_samples: int = 3
    fitness_window_size: int = 10

    # ─── SANDBOX ──────────────────────────────────────────────────────────────
    sandbox_cpu_quota: int = 50000
    sandbox_cpu_period: int = 100000
    sandbox_mem_limit: str = "256m"
    sandbox_timeout_sec: int = 30
    sandbox_network: str = "none"
    sandbox_base_image: str = "python:3.12-slim"
    max_genome_size_kb: int = 512

    # ─── WORKER ───────────────────────────────────────────────────────────────
    worker_concurrency: int = 4
    worker_queue_poll_interval: float = 0.5

    # ─── METRICS ──────────────────────────────────────────────────────────────
    metrics_enabled: bool = True
    telemetry_flush_interval: int = 5

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        return self.environment == "development"


settings = Settings()
