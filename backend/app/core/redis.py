# mycelium/backend/app/core/redis.py

import json
from typing import Any, AsyncGenerator, Callable, Optional

import redis.asyncio as aioredis
from redis.asyncio import Redis
from redis.asyncio.client import PubSub

from .config import settings
from .logging import get_logger

logger = get_logger(__name__)

# Module-level connection pools
_redis_client: Optional[Redis] = None
_redis_queue_client: Optional[Redis] = None


async def get_redis() -> Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = await aioredis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
            max_connections=20,
        )
        logger.info("redis.connected", url=settings.redis_url)
    return _redis_client


async def get_queue_redis() -> Redis:
    global _redis_queue_client
    if _redis_queue_client is None:
        _redis_queue_client = await aioredis.from_url(
            settings.redis_queue_url,
            encoding="utf-8",
            decode_responses=True,
            max_connections=10,
        )
        logger.info("redis.queue.connected", url=settings.redis_queue_url)
    return _redis_queue_client


async def close_redis() -> None:
    global _redis_client, _redis_queue_client
    if _redis_client:
        await _redis_client.aclose()
        _redis_client = None
    if _redis_queue_client:
        await _redis_queue_client.aclose()
        _redis_queue_client = None
    logger.info("redis.closed")


class EventBus:
    """
    Redis pub/sub event bus for broadcasting MYCELIUM events
    to all connected WebSocket clients and internal subscribers.
    """

    CHANNEL = settings.redis_event_channel

    def __init__(self, redis: Redis):
        self._redis = redis

    async def publish(self, event: Any) -> int:
        """Publish an EventEnvelope to the event bus."""
        if hasattr(event, "to_json"):
            payload = event.to_json()
        elif isinstance(event, dict):
            payload = json.dumps(event)
        else:
            payload = str(event)

        count = await self._redis.publish(self.CHANNEL, payload)
        logger.debug("event.published", channel=self.CHANNEL, subscribers=count)
        return count

    async def subscribe(self) -> PubSub:
        """Return a PubSub object subscribed to the event channel."""
        pubsub = self._redis.pubsub()
        await pubsub.subscribe(self.CHANNEL)
        return pubsub

    async def stream_events(
        self, pubsub: PubSub
    ) -> AsyncGenerator[str, None]:
        """Async generator yielding raw JSON event strings."""
        async for message in pubsub.listen():
            if message["type"] == "message":
                yield message["data"]


class WorkerQueue:
    """
    Redis-backed task queue for dispatching work to evolution workers.
    Uses sorted sets for priority queuing.
    """

    QUEUE_KEY = "mycelium:tasks"
    PROCESSING_KEY = "mycelium:tasks:processing"
    DEAD_LETTER_KEY = "mycelium:tasks:dead"

    def __init__(self, redis: Redis):
        self._redis = redis

    async def enqueue(self, task: Any, priority: int = 5) -> str:
        """Push a task onto the priority queue. Returns task ID."""
        if hasattr(task, "to_json"):
            payload = task.to_json()
        else:
            payload = json.dumps(task)

        task_id = json.loads(payload).get("id", "unknown")
        # Score = timestamp - (priority * 1000) so higher priority = lower score = dequeued first
        import time
        score = time.time() - (priority * 1000)
        await self._redis.zadd(self.QUEUE_KEY, {payload: score})
        logger.debug("task.enqueued", task_id=task_id, priority=priority)
        return task_id

    async def dequeue(self, timeout: float = 1.0) -> Optional[str]:
        """Non-blocking dequeue. Returns raw JSON string or None."""
        result = await self._redis.zpopmin(self.QUEUE_KEY, count=1)
        if result:
            payload, score = result[0]
            return payload
        return None

    async def queue_depth(self) -> int:
        return await self._redis.zcard(self.QUEUE_KEY)

    async def dead_letter(self, payload: str, reason: str) -> None:
        """Move failed task to dead letter queue."""
        import time
        await self._redis.zadd(
            self.DEAD_LETTER_KEY,
            {json.dumps({"payload": payload, "reason": reason, "ts": time.time()}): time.time()}
        )
