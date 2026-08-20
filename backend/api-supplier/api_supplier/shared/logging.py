from __future__ import annotations

import json
import logging
from datetime import UTC, datetime

from .observability import (
    current_trace_fields,
    get_correlation_id,
)


_RESERVED = {
    "name",
    "msg",
    "args",
    "levelname",
    "levelno",
    "pathname",
    "filename",
    "module",
    "exc_info",
    "exc_text",
    "stack_info",
    "lineno",
    "funcName",
    "created",
    "msecs",
    "relativeCreated",
    "thread",
    "threadName",
    "processName",
    "process",
    "taskName",
    "message",
    "asctime",
}


class JsonFormatter(logging.Formatter):
    def __init__(
        self,
        service_name: str,
    ) -> None:
        super().__init__()
        self._service_name = service_name

    def format(
        self,
        record: logging.LogRecord,
    ) -> str:
        data = {
            "timestamp": datetime.now(
                UTC
            ).isoformat(),
            "level": record.levelname,
            "service": self._service_name,
            "logger": record.name,
            "message": record.getMessage(),
            "correlation_id": (
                get_correlation_id()
            ),
        }

        data.update(current_trace_fields())

        for key, value in (
            record.__dict__.items()
        ):
            if (
                key not in _RESERVED
                and not key.startswith("_")
            ):
                data[key] = value

        if record.exc_info:
            data["exception"] = (
                self.formatException(
                    record.exc_info
                )
            )

        return json.dumps(
            data,
            default=str,
            separators=(",", ":"),
        )


def configure_logging(
    service_name: str,
    level: str | None = None,
) -> logging.Logger:
    configured_level = (
        level
        or os_level()
    )

    handler = logging.StreamHandler()
    handler.setFormatter(
        JsonFormatter(service_name)
    )

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(
        getattr(
            logging,
            configured_level.upper(),
            logging.INFO,
        )
    )

    return logging.getLogger(service_name)


def os_level() -> str:
    import os

    return os.getenv(
        "LOG_LEVEL",
        "INFO",
    )
