# mycelium/backend/app/core/logging.py

import logging
import sys
from typing import Any, Dict

import structlog
from structlog.types import EventDict, Processor

from .config import settings


def add_service_context(
    logger: Any, method: str, event_dict: EventDict
) -> EventDict:
    event_dict["service"] = "mycelium-backend"
    event_dict["environment"] = settings.environment
    return event_dict


def drop_color_message_key(
    logger: Any, method: str, event_dict: EventDict
) -> EventDict:
    """Remove uvicorn's color_message key which duplicates 'message'."""
    event_dict.pop("color_message", None)
    return event_dict


def setup_logging() -> None:
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        add_service_context,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        drop_color_message_key,
    ]

    if settings.is_production:
        processors = shared_processors + [
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer(),
        ]
    else:
        processors = shared_processors + [
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.StackInfoRenderer(),
            structlog.dev.ConsoleRenderer(colors=True),
        ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, settings.log_level.upper(), logging.DEBUG)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )

    # Configure stdlib logging to route through structlog
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level.upper(), logging.DEBUG),
    )

    # Silence noisy libs
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("aiohttp").setLevel(logging.WARNING)


def get_logger(name: str) -> structlog.BoundLogger:
    return structlog.get_logger(name)
