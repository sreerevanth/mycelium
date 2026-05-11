# mycelium/backend/app/api/ws.py
# WebSocket endpoint for real-time event streaming

import asyncio
import json
import time
from typing import Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from redis.asyncio.client import PubSub

from app.core.redis import get_redis, EventBus
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/ws", tags=["websocket"])


class ConnectionManager:
    """Manages active WebSocket connections."""

    def __init__(self) -> None:
        self._connections: dict[str, WebSocket] = {}

    async def connect(self, connection_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections[connection_id] = websocket
        logger.info("ws.connected", connection_id=connection_id, total=len(self._connections))

    def disconnect(self, connection_id: str) -> None:
        self._connections.pop(connection_id, None)
        logger.info("ws.disconnected", connection_id=connection_id, total=len(self._connections))

    async def send_json(self, connection_id: str, data: dict) -> None:
        ws = self._connections.get(connection_id)
        if ws:
            try:
                await ws.send_json(data)
            except Exception:
                self.disconnect(connection_id)

    async def broadcast_json(self, data: dict) -> None:
        dead = []
        for cid, ws in self._connections.items():
            try:
                await ws.send_json(data)
            except Exception:
                dead.append(cid)
        for cid in dead:
            self.disconnect(cid)

    @property
    def connection_count(self) -> int:
        return len(self._connections)


manager = ConnectionManager()


@router.websocket("/events")
async def event_stream(
    websocket: WebSocket,
    filter_types: Optional[str] = Query(None, description="Comma-separated event types to filter"),
):
    """
    WebSocket endpoint that streams all MYCELIUM evolution events.
    Clients subscribe and receive real-time genome/mutation/benchmark events.
    """
    import uuid
    connection_id = str(uuid.uuid4())
    allowed_types = set(filter_types.split(",")) if filter_types else None

    await manager.connect(connection_id, websocket)

    # Send handshake
    await websocket.send_json({
        "type": "system.connected",
        "connection_id": connection_id,
        "timestamp": time.time(),
        "filters": list(allowed_types) if allowed_types else None,
    })

    redis = await get_redis()
    event_bus = EventBus(redis)
    pubsub: PubSub = await event_bus.subscribe()

    try:
        async for raw_event in event_bus.stream_events(pubsub):
            try:
                event = json.loads(raw_event)

                # Apply type filter if specified
                if allowed_types and event.get("type") not in allowed_types:
                    continue

                await websocket.send_json(event)

            except json.JSONDecodeError:
                logger.warning("ws.invalid_event", raw=raw_event[:100])
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error("ws.send_error", error=str(e))
                break

    except WebSocketDisconnect:
        pass
    except asyncio.CancelledError:
        pass
    finally:
        await pubsub.unsubscribe()
        await pubsub.aclose()
        manager.disconnect(connection_id)


@router.websocket("/status")
async def status_stream(websocket: WebSocket):
    """
    Lightweight WebSocket for system status heartbeats.
    Sends worker count, queue depth, and active genome count every 2 seconds.
    """
    import uuid
    connection_id = str(uuid.uuid4())
    await websocket.accept()
    logger.info("ws.status.connected", connection_id=connection_id)

    try:
        redis = await get_redis()
        while True:
            try:
                queue_depth = await redis.zcard("mycelium:tasks")
                await websocket.send_json({
                    "type": "system.status",
                    "timestamp": time.time(),
                    "queue_depth": queue_depth,
                    "ws_connections": manager.connection_count,
                })
                await asyncio.sleep(2.0)
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error("ws.status.error", error=str(e))
                break
    finally:
        logger.info("ws.status.disconnected", connection_id=connection_id)
