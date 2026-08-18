from api_supplier.bootstrap.settings import get_settings
from api_supplier.infrastructure.retrieval.opensearch.client import (
    create_opensearch_client,
)
from api_supplier.infrastructure.retrieval.opensearch.policy_index import OpenSearchPolicyIndexInitializer


async def main() -> None:
    settings = get_settings()

    client = create_opensearch_client(
        endpoint=settings.opensearch_endpoint,
        region=settings.aws_region,
        service=settings.opensearch_service,
    )

    initializer = OpenSearchPolicyIndexInitializer(
        client,
        index_name=settings.opensearch_index_name,
        dimensions=settings.embedding_dimensions,
    )

    await initializer.ensure_exists()

    print(
        f"Index '{settings.opensearch_index_name}' is ready."
    )


if __name__ == "__main__":
    import asyncio

    asyncio.run( main())