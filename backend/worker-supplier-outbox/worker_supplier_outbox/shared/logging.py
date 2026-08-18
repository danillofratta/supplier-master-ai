import json
import logging
from datetime import UTC, datetime


_RESERVED = {
    "name", "msg", "args", "levelname", "levelno", "pathname",
    "filename", "module", "exc_info", "exc_text", "stack_info",
    "lineno", "funcName", "created", "msecs", "relativeCreated",
    "thread", "threadName", "processName", "process", "taskName",
}


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        data = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        for key, value in record.__dict__.items():
            if key not in _RESERVED and not key.startswith("_"):
                data[key] = value

        if record.exc_info:
            data["exception"] = self.formatException(
                record.exc_info
            )

        return json.dumps(
            data,
            default=str,
            separators=(",", ":"),
        )


def configure_logging(
    service_name: str,
    level: str = "INFO",
) -> logging.Logger:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(
        getattr(logging, level.upper(), logging.INFO)
    )

    return logging.getLogger(service_name)
