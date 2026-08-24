from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


_SERVICE_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_SERVICE_ROOT / ".env")


def _csv(name: str, default: str) -> tuple[str, ...]:
    raw = os.getenv(name, default)
    return tuple(
        item.strip()
        for item in raw.split(",")
        if item.strip()
    )


@dataclass(frozen=True, slots=True)
class Settings:
    gateway_url: str
    api_prefix: str
    http_timeout_seconds: float
    transport: str
    host: str
    port: int
    allowed_hosts: tuple[str, ...]
    allowed_origins: tuple[str, ...]

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            gateway_url=os.getenv(
                "SUPPLIER_GATEWAY_URL",
                "http://127.0.0.1:8000",
            ).rstrip("/"),
            api_prefix=os.getenv(
                "SUPPLIER_API_PREFIX",
                "/api/v1",
            ).rstrip("/"),
            http_timeout_seconds=float(
                os.getenv(
                    "SUPPLIER_API_TIMEOUT_SECONDS",
                    "60",
                )
            ),
            transport=os.getenv(
                "MCP_TRANSPORT",
                "stdio",
            ).strip().lower(),
            host=os.getenv(
                "MCP_HOST",
                "127.0.0.1",
            ),
            port=int(
                os.getenv(
                    "MCP_PORT",
                    "8010",
                )
            ),
            allowed_hosts=_csv(
                "MCP_ALLOWED_HOSTS",
                "localhost,localhost:8010,127.0.0.1,127.0.0.1:8010,mcp-supplier,mcp-supplier:8010",
            ),
            allowed_origins=_csv(
                "MCP_ALLOWED_ORIGINS",
                "http://localhost:6274,http://127.0.0.1:6274",
            ),
        )
