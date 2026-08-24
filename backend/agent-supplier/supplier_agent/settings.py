from functools import lru_cache

from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class Settings(BaseSettings):
    aws_region: str
    bedrock_model_id: str

    langgraph_database_url: str

    supplier_mcp_url: str = (
        "http://127.0.0.1:8010/mcp"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()