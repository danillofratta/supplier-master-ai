import asyncio

from backend.app.bootstrap.settings import get_settings
from backend.app.infrastructure.ai.bedrock.titan_embedding_provider import (
    TitanEmbeddingProvider,
)
from backend.app.infrastructure.retrieval.opensearch.client import (
    create_opensearch_client,
)
from backend.app.infrastructure.retrieval.opensearch.policy_retriever import (
    OpenSearchPolicyRetriever,
)


async def main() -> None:
    settings = get_settings()

    embedding_provider = TitanEmbeddingProvider(
        region_name=settings.aws_region,
        model_id=settings.embedding_model_id,
        dimensions=settings.embedding_dimensions,
    )

    client = create_opensearch_client(
        endpoint=settings.opensearch_endpoint,
        region=settings.aws_region,
        service=settings.opensearch_service,
    )

    retriever = OpenSearchPolicyRetriever(
        client=client,
        embedding_provider=embedding_provider,
        index_name=settings.opensearch_index_name,
    )

    queries = [
        "What happens with a foreign vendor?",
        "What proof is required for the supplier's bank account?",
        "What happens when mandatory documents are missing?",
        "What happens with a high-risk supplier?",
    ]

    for query in queries:
        results = await retriever.retrieve(query, limit=3)
        print(f"Query: {query}")
        print(f"Results: {len(results)}")
        for index, policy in enumerate(results, start=1):
            print()
            print(f"Result #{index}")
            print(f"Score: {policy.score}")
            print(f"Document: {policy.document_id}")
            print(f"Chunk: {policy.chunk_id}")
            print(f"Title: {policy.title}")
            print("Content:")
            print(policy.content)
        print("\n" + "=" * 80 + "\n")

    # results = await retriever.retrieve(
    #     "What happens with a foreign vendor?",
    #     limit=3,
    # )

    # print(f"Results: {len(results)}")

    # for index, policy in enumerate(results, start=1):
    #     print()
    #     print(f"Result #{index}")
    #     print(f"Score: {policy.score}")
    #     print(f"Document: {policy.document_id}")
    #     print(f"Chunk: {policy.chunk_id}")
    #     print(f"Title: {policy.title}")
    #     print("Content:")
    #     print(policy.content)


if __name__ == "__main__":
    asyncio.run(main())