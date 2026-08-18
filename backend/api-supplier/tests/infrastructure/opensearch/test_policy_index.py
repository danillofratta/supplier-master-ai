import pytest

from api_supplier.features.policies.ingest.indexed_policy_chunk import IndexedPolicyChunk
from api_supplier.features.policies.ingest.policy_chunk import PolicyChunk
from api_supplier.infrastructure.retrieval.opensearch.index_mapping import (
    build_policy_index_mapping,
)
from api_supplier.infrastructure.retrieval.opensearch.policy_index import (
    OpenSearchPolicyIndex,
    OpenSearchPolicyIndexInitializer,
)


class FakeIndices:
    def __init__(self, exists: bool = False) -> None:
        self._exists = exists
        self.created = None

    def exists(self, *, index):
        return self._exists

    def create(self, *, index, body):
        self.created = (index, body)


class FakeOpenSearchClient:
    def __init__(self) -> None:
        self.indices = FakeIndices()
        self.indexed: list[dict] = []

    def index(self, **kwargs):
        self.indexed.append(kwargs)


@pytest.mark.asyncio
async def test_initializer_creates_vector_index_with_matching_dimensions() -> None:
    client = FakeOpenSearchClient()
    initializer = OpenSearchPolicyIndexInitializer(
        client,
        index_name="policies",
        dimensions=3,
    )

    await initializer.ensure_exists()

    index_name, mapping = client.indices.created
    assert index_name == "policies"
    assert mapping["mappings"]["properties"]["embedding"]["dimension"] == 3
    assert mapping["mappings"]["properties"]["embedding"]["method"]["name"] == "hnsw"


@pytest.mark.asyncio
async def test_policy_index_uses_stable_chunk_id_as_document_id() -> None:
    client = FakeOpenSearchClient()
    policy_index = OpenSearchPolicyIndex(client, index_name="policies")
    chunk = PolicyChunk(
        document_id="policy-001",
        chunk_id="policy-001:0001",
        title="Supplier Policy",
        content="International suppliers require manual review.",
        policy_type="supplier_onboarding",
        version="1.0",
        effective_date="2026-01-01",
        position=1,
    )

    await policy_index.upsert((IndexedPolicyChunk(chunk=chunk, embedding=(0.1, 0.2, 0.3)),))

    assert client.indexed[0]["id"] == "policy-001:0001"
    assert client.indexed[0]["body"]["embedding"] == [0.1, 0.2, 0.3]


def test_mapping_rejects_invalid_dimension() -> None:
    with pytest.raises(ValueError):
        build_policy_index_mapping(dimensions=0)
