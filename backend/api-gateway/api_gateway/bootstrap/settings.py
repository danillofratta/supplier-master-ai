import os
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True, slots=True)
class Settings:
    supplier_api_url: str
    supplier_api_timeout_seconds: float
    cors_origins: tuple[str, ...]


@lru_cache
def get_settings() -> Settings:
    origins = tuple(
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173,"
            "http://localhost:3000,http://127.0.0.1:3000",
        ).split(",")
        if origin.strip()
    )

    return Settings(
        supplier_api_url=os.getenv(
            "SUPPLIER_API_URL",
            "http://127.0.0.1:8001",
        ).rstrip("/"),
        supplier_api_timeout_seconds=float(
            os.getenv(
                "SUPPLIER_API_TIMEOUT_SECONDS",
                "10",
            )
        ),
        cors_origins=origins,
    )
