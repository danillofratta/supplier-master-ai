import asyncio
from pathlib import Path

from api_supplier.bootstrap.settings import get_settings
from api_supplier.features.policies.ingest.command import IngestPolicyCommand
from api_supplier.features.policies.ingest.handler import IngestPolicyHandler
from api_supplier.infrastructure.ai.bedrock.titan_embedding_provider import (
    TitanEmbeddingProvider,
)
from api_supplier.infrastructure.retrieval.opensearch.client import (
    create_opensearch_client,
)
from api_supplier.infrastructure.retrieval.opensearch.policy_index import (
    OpenSearchPolicyIndex,
)
from api_supplier.infrastructure.retrieval.semantic_document_chunker import SemanticDocumentChunker
from api_supplier.infrastructure.retrieval.simple_document_chunker import (
    SimpleDocumentChunker,
)


async def main() -> None:
    settings = get_settings()

    content = Path(
        "sample-data/policies/supplier_onboarding_policy.txt"
    ).read_text(encoding="utf-8")

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

    policy_index = OpenSearchPolicyIndex(
        client=client,
        index_name=settings.opensearch_index_name,
    )

    handler = IngestPolicyHandler(
        # chunker=SimpleDocumentChunker(
        #     max_characters=200,
        #     overlap_characters=40,
        # ),
        chunker=SemanticDocumentChunker(
            max_characters=220,
            overlap_sentences=1,
        ),
        embedding_provider=embedding_provider,
        policy_index=policy_index,
    )

    result = await handler.handle(
        IngestPolicyCommand(
            document_id="supplier-onboarding-001",
            title="Supplier Onboarding Policy",
            content=content,
            policy_type="supplier_onboarding",
            version="1.0",
            effective_date="2026-01-01",
        )
    )

    print("Policy successfully ingested")
    print("Document:", result.document_id)
    print("Chunks:", result.chunks_indexed)
    print("Embedding dimensions:", result.embedding_dimensions)


if __name__ == "__main__":
    asyncio.run(main())