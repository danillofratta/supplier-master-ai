from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


_SERVICE_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    aws_region: str = "us-east-2"
    bedrock_model_id: str | None = None

    langgraph_database_url: str = (
        "postgresql://postgres:postgres@localhost:5432/supplier_agent_db"
    )
    supplier_mcp_url: str = "http://127.0.0.1:8010/mcp"

    agent_ai_provider: Literal[
        "bedrock",
        "openai",
        "gemini",
    ] = "bedrock"
    agent_temperature: float = Field(default=0.1, ge=0.0, le=1.0)
    agent_max_tokens: int = Field(default=1500, gt=0)

    openai_api_key: str | None = None
    openai_model: str | None = None

    google_api_key: str | None = None
    gemini_model: str | None = None

    agent_api_host: str = "127.0.0.1"
    agent_api_port: int = Field(default=8011, ge=1, le=65535)
    agent_api_cors_origins: str = (
        "http://localhost:5173,http://127.0.0.1:5173"
    )

    @property
    def cors_origins(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.agent_api_cors_origins.split(",")
            if origin.strip()
        ]

    model_config = SettingsConfigDict(
        env_file=_SERVICE_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
