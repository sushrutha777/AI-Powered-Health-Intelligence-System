"""
Structured logging configuration.

Provides JSON-formatted structured logs in production and
human-readable colored logs in development. Sanitizes sensitive
data (PHI, credentials) from log output.
"""

import logging
import sys
from typing import Any

import structlog

from src.core.config import get_settings

# Fields that must never appear in logs
_SENSITIVE_FIELDS = frozenset({
    "password",
    "hashed_password",
    "token",
    "access_token",
    "secret",
    "api_key",
    "authorization",
    "ssn",
    "social_security",
    "medical_record",
    "patient_name",
    "dob",
    "date_of_birth",
})


def _sanitize_event(
    logger: Any, method_name: str, event_dict: dict[str, Any]
) -> dict[str, Any]:
    """
    Remove sensitive fields from log events to prevent PHI leakage.

    Recursively checks all keys in the event dictionary and redacts
    any that match known sensitive field names.
    """
    for key in list(event_dict.keys()):
        if key.lower() in _SENSITIVE_FIELDS:
            event_dict[key] = "***REDACTED***"
        elif isinstance(event_dict[key], dict):
            event_dict[key] = {
                k: "***REDACTED***" if k.lower() in _SENSITIVE_FIELDS else v
                for k, v in event_dict[key].items()
            }
    return event_dict


def setup_logging() -> None:
    """
    Configure structured logging for the application.

    - Development: colored, human-readable console output
    - Production: JSON-formatted logs for log aggregation systems
    """
    settings = get_settings()
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    # Shared processors for all environments
    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
        _sanitize_event,
    ]

    if settings.is_production:
        # JSON logs for production log aggregation
        renderer = structlog.processors.JSONRenderer()
    else:
        # Colored console output for development
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Configure standard library logging to use structlog formatting
    formatter = structlog.stdlib.ProcessorFormatter(
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(log_level)

    # Suppress noisy third-party loggers
    for logger_name in ("uvicorn.access", "sqlalchemy.engine", "httpx"):
        logging.getLogger(logger_name).setLevel(logging.WARNING)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a named structured logger instance."""
    return structlog.get_logger(name)
