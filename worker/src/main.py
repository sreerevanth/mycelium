# mycelium/worker/src/main.py
# Worker process entrypoint - connects to Redis queue and processes evolution tasks

import asyncio
import os
import signal
import sys
import time
import uuid
from typing import Optional

import redis.asyncio as aioredis
import structlog
from pydantic_settings import BaseSettings

structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer(colors=True),
    ]
)
logger = structlog.get_logger(__name__)


class WorkerSettings(BaseSettings):
    redis_queue_url: str = "redis://redis:6379/1"
    redis_url: str = "redis://redis:6379/0"
    redis_event_channel: str = "mycelium:events"
    worker_id: str = f"worker-{uuid.uuid4().hex[:8]}"
    worker_concurrency: int = 4
    worker_queue_poll_interval: float = 0.5
    sandbox_timeout_sec: int = 30
    log_level: str = "DEBUG"
    environment: str = "development"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = WorkerSettings()


class Worker:
    """
    Evolution worker process.
    Polls the Redis task queue and executes evolution tasks concurrently.
    """

    QUEUE_KEY = "mycelium:tasks"

    def __init__(self) -> None:
        self.worker_id = settings.worker_id
        self._running = False
        self._tasks: set[asyncio.Task] = set()
        self._redis: Optional[aioredis.Redis] = None
        self._semaphore = asyncio.Semaphore(settings.worker_concurrency)

    async def _connect(self) -> None:
        self._redis = await aioredis.from_url(
            settings.redis_queue_url,
            encoding="utf-8",
            decode_responses=True,
        )
        await self._redis.ping()
        logger.info("worker.redis.connected", worker_id=self.worker_id)

    async def _announce(self, status: str) -> None:
        """Publish worker presence event to the event bus."""
        import json
        event_redis = await aioredis.from_url(
            settings.redis_url, encoding="utf-8", decode_responses=True
        )
        event = {
            "id": str(uuid.uuid4()),
            "type": f"worker.{status}",
            "timestamp": time.time(),
            "source": self.worker_id,
            "payload": {
                "worker_id": self.worker_id,
                "concurrency": settings.worker_concurrency,
                "status": status,
            },
        }
        await event_redis.publish(settings.redis_event_channel, json.dumps(event))
        await event_redis.aclose()

    async def _process_task(self, raw_payload: str) -> None:
        """Process a single task from the queue."""
        import json
        async with self._semaphore:
            try:
                task = json.loads(raw_payload)
                task_type = task.get("task_type", "unknown")
                task_id = task.get("id", "unknown")

                logger.info(
                    "task.processing",
                    worker_id=self.worker_id,
                    task_id=task_id,
                    task_type=task_type,
                )

                # Dispatch to appropriate handler
                handler = self._get_handler(task_type)
                if handler:
                    await handler(task)
                else:
                    logger.warning(
                        "task.unknown_type",
                        task_type=task_type,
                        task_id=task_id,
                    )

            except json.JSONDecodeError as e:
                logger.error("task.parse_error", error=str(e))
            except Exception as e:
                logger.error("task.processing_error", error=str(e), exc_info=True)

    def _get_handler(self, task_type: str):
        handlers = {
            "mutate": self._handle_mutate,
            "benchmark": self._handle_benchmark,
            "evaluate": self._handle_evaluate,
            "evolve_cycle": self._handle_evolve_cycle,
        }
        return handlers.get(task_type)

    async def _handle_mutate(self, task: dict) -> None:
        """Placeholder: full implementation in Phase 3."""
        logger.info("task.mutate", genome_id=task.get("payload", {}).get("genome_id"))
        await asyncio.sleep(0.1)  # simulate work

    async def _handle_benchmark(self, task: dict) -> None:
        """Placeholder: full implementation in Phase 4/5."""
        logger.info("task.benchmark", genome_id=task.get("payload", {}).get("genome_id"))
        await asyncio.sleep(0.1)

    async def _handle_evaluate(self, task: dict) -> None:
        """Placeholder: full implementation in Phase 5."""
        logger.info("task.evaluate", genome_id=task.get("payload", {}).get("genome_id"))
        await asyncio.sleep(0.1)

    async def _handle_evolve_cycle(self, task: dict) -> None:
        """Placeholder: full implementation in Phase 8."""
        logger.info("task.evolve_cycle", cycle_id=task.get("payload", {}).get("cycle_id"))
        await asyncio.sleep(0.1)

    async def _poll_loop(self) -> None:
        """Main polling loop - dequeues and dispatches tasks."""
        logger.info("worker.polling", worker_id=self.worker_id)
        while self._running:
            try:
                result = await self._redis.zpopmin(self.QUEUE_KEY, count=1)
                if result:
                    raw_payload, score = result[0]
                    task_coro = self._process_task(raw_payload)
                    task = asyncio.create_task(task_coro)
                    self._tasks.add(task)
                    task.add_done_callback(self._tasks.discard)
                else:
                    await asyncio.sleep(settings.worker_queue_poll_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("worker.poll_error", error=str(e))
                await asyncio.sleep(1.0)

    async def start(self) -> None:
        await self._connect()
        self._running = True
        await self._announce("online")
        logger.info(
            "worker.started",
            worker_id=self.worker_id,
            concurrency=settings.worker_concurrency,
        )
        await self._poll_loop()

    async def stop(self) -> None:
        logger.info("worker.stopping", worker_id=self.worker_id)
        self._running = False

        # Wait for in-flight tasks
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)

        await self._announce("offline")

        if self._redis:
            await self._redis.aclose()

        logger.info("worker.stopped", worker_id=self.worker_id)


async def main() -> None:
    worker = Worker()

    loop = asyncio.get_running_loop()

    def _shutdown(sig):
        logger.info("worker.signal_received", signal=sig.name)
        asyncio.create_task(worker.stop())

    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, _shutdown, sig)

    await worker.start()


if __name__ == "__main__":
    asyncio.run(main())
