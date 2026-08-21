from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    aws_region: str = "us-east-2"

    bedrock_model_id: str | None = None
    bedrock_temperature: float = Field(default=0.0, ge=0.0, le=1.0)
    bedrock_max_tokens: int = Field(default=1000, gt=0)

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/supplier_db"

    opensearch_endpoint: str | None = None
    opensearch_index_name: str = "supplier-policies"
    opensearch_service: str = "aoss"

    embedding_model_id: str = "amazon.titan-embed-text-v2:0"
    embedding_dimensions: int = 1024

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
