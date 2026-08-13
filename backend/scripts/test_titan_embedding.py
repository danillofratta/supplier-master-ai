from backend.app.bootstrap.settings import get_settings
from backend.app.infrastructure.ai.bedrock.titan_embedding_provider import TitanEmbeddingProvider


async def main() -> None:
    settings = get_settings()

    provider = TitanEmbeddingProvider(
        model_id=settings.embedding_model_id,
        region_name=settings.aws_region,
        dimensions=settings.embedding_dimensions,
    )

    embedding = await provider.generate(
        "International suppliers require manual compliance review."
    )

    print("Dimensions:", len(embedding))
    print("Firs values:"), print(embedding[:10])

if __name__ == "__main__":
    import asyncio

    asyncio.run(main())