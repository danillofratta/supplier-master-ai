import pytest

from api_supplier.features.policies.ingest.command import (
    IngestPolicyCommand,
)
from api_supplier.features.policies.ingest.handler import (
    IngestPolicyHandler,
)
from api_supplier.infrastructure.retrieval.simple_document_chunker import (
    SimpleDocumentChunker,
)


class FakeEmbeddingProvider:
    dimensions = 3

    def __init__(self) -> None:
        self.calls = 0

    async def generate(
        self,
        text: str,
    ) -> tuple[float, ...]:
        self.calls += 1
        return (1.0, 2.0, 3.0)


class FailingEmbeddingProvider(FakeEmbeddingProvider):
    async def generate(
        self,
        text: str,
    ) -> tuple[float, ...]:
        raise RuntimeError("embedding unavailable")


class FakePolicyIndex:
    def __init__(self) -> None:
        self.deleted: list[tuple[str, str]] = []
        self.upserted = ()

    async def delete_document(
        self,
        document_id: str,
        version: str,
    ) -> None:
        self.deleted.append(
            (document_id, version)
        )

    async def upsert(self, chunks) -> None:
        self.upserted = chunks


def command() -> IngestPolicyCommand:
    return IngestPolicyCommand(
        document_id="supplier-onboarding-001",
        title="Supplier Onboarding",
        content="Required compliance evidence and approval rules.",
        policy_type="supplier_onboarding",
        version="1.0",
        effective_date="2026-08-21",
    )


@pytest.mark.asyncio
async def test_ingest_replaces_document_after_embeddings_are_ready() -> None:
    provider = FakeEmbeddingProvider()
    index = FakePolicyIndex()
    handler = IngestPolicyHandler(
        chunker=SimpleDocumentChunker(),
        embedding_provider=provider,
        policy_index=index,
    )

    result = await handler.handle(command())

    assert result.document_id == "supplier-onboarding-001"
    assert result.chunks_indexed == 1
    assert provider.calls == 1
    assert index.deleted == [
        ("supplier-onboarding-001", "1.0")
    ]
    assert len(index.upserted) == 1


@pytest.mark.asyncio
async def test_embedding_failure_does_not_delete_existing_policy() -> None:
    index = FakePolicyIndex()
    handler = IngestPolicyHandler(
        chunker=SimpleDocumentChunker(),
        embedding_provider=FailingEmbeddingProvider(),
        policy_index=index,
    )

    with pytest.raises(
        RuntimeError,
        match="embedding unavailable",
    ):
        await handler.handle(command())

    assert index.deleted == []
    assert index.upserted == ()
