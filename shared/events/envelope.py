# mycelium/shared/events/envelope.py
# Wire protocol envelope for all MYCELIUM events

from __future__ import annotations

import time
import uuid
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from .types import EventType


class EventEnvelope(BaseModel):
    """
    Canonical wire format for all MYCELIUM internal events.
    Used by Redis pub/sub, WebSocket streams, and worker queues.
    """

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: EventType
    timestamp: float = Field(default_factory=time.time)
    source: str  # service identifier: "backend", "worker-01", "evolution-engine"
    session_id: Optional[str] = None  # evolution cycle session
    correlation_id: Optional[str] = None  # trace across related events
    payload: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        use_enum_values = True

    @classmethod
    def create(
        cls,
        event_type: EventType,
        source: str,
        payload: Dict[str, Any],
        *,
        session_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "EventEnvelope":
        return cls(
            type=event_type,
            source=source,
            payload=payload,
            session_id=session_id,
            correlation_id=correlation_id,
            metadata=metadata or {},
        )

    def to_json(self) -> str:
        return self.model_dump_json()

    @classmethod
    def from_json(cls, data: str) -> "EventEnvelope":
        return cls.model_validate_json(data)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()


class TaskEnvelope(BaseModel):
    """
    Worker task queue message format.
    Wraps work items dispatched to evolution workers.
    """

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    task_type: str  # "mutate", "benchmark", "evaluate", "evolve_cycle"
    priority: int = Field(default=5, ge=0, le=10)
    enqueued_at: float = Field(default_factory=time.time)
    deadline: Optional[float] = None  # unix timestamp
    retry_count: int = 0
    max_retries: int = 3
    payload: Dict[str, Any] = Field(default_factory=dict)
    routing_key: Optional[str] = None  # target specific worker

    class Config:
        use_enum_values = True

    def is_expired(self) -> bool:
        if self.deadline is None:
            return False
        return time.time() > self.deadline

    def to_json(self) -> str:
        return self.model_dump_json()

    @classmethod
    def from_json(cls, data: str) -> "TaskEnvelope":
        return cls.model_validate_json(data)
