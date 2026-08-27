from typing import Any

from langchain_aws import ChatBedrockConverse

from supplier_agent.settings import Settings


def build_chat_model(settings: Settings) -> Any:
    """Build the chat model selected for the agent runtime.

    Bedrock remains the default provider. OpenAI and Gemini are loaded lazily
    so the existing Bedrock setup keeps working without additional packages.
    """

    provider = settings.agent_ai_provider

    if provider == "bedrock":
        if not settings.bedrock_model_id:
            raise ValueError(
                "BEDROCK_MODEL_ID is required when AGENT_AI_PROVIDER=bedrock."
            )

        return ChatBedrockConverse(
            model=settings.bedrock_model_id,
            region_name=settings.aws_region,
            temperature=settings.agent_temperature,
            max_tokens=settings.agent_max_tokens,
        )

    if provider == "openai":
        if not settings.openai_api_key or not settings.openai_model:
            raise ValueError(
                "OPENAI_API_KEY and OPENAI_MODEL are required when "
                "AGENT_AI_PROVIDER=openai."
            )

        try:
            from langchain_openai import ChatOpenAI
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "OpenAI support is not installed. Install the agent "
                "with the 'openai' optional dependency."
            ) from exc

        return ChatOpenAI(
            model=settings.openai_model,
            api_key=settings.openai_api_key,
            temperature=settings.agent_temperature,
            max_tokens=settings.agent_max_tokens,
        )

    if provider == "gemini":
        if not settings.google_api_key or not settings.gemini_model:
            raise ValueError(
                "GOOGLE_API_KEY and GEMINI_MODEL are required when "
                "AGENT_AI_PROVIDER=gemini."
            )

        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "Gemini support is not installed. Install the agent "
                "with the 'gemini' optional dependency."
            ) from exc

        return ChatGoogleGenerativeAI(
            model=settings.gemini_model,
            google_api_key=settings.google_api_key,
            temperature=settings.agent_temperature,
            max_output_tokens=settings.agent_max_tokens,
        )

    raise ValueError(f"Unsupported agent AI provider: {provider}")
