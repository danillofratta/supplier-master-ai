from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    aws_region: str
    bedrock_model_id: str
    mcp_server_url: str