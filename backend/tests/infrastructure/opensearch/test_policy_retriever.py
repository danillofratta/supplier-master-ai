import pytest

from backend.app.infrastructure.retrieval.opensearch.policy_retriever import (
    OpenSearchPolicyRetriever,
)


class FakeEmbeddingProvider:
    dimensions = 3

    def __init__(self) -> None:
        self.received_texts: list[str] = []

    async def generate(self, text: str) -> tuple[float, ...]:
        self.received_texts.append(text)
        return (0.1, 0.2, 0.3)


class FakeOpenSearchClient:
    def __init__(self) -> None:
        self.received_index = None
        self.received_body = None

    def search(self, *, index, body):
        self.received_index = index
        self.received_body = body
        return {
            "hits": {
                "hits": [
                    {
                        "_score": 0.95,
                        "_source": {
                            "document_id": "policy-001",
                            "chunk_id": "policy-001:0001",
                            "title": "Bank Policy",
                            "content": "Bank ownership confirmation is mandatory.",
                            "policy_type": "compliance",
                            "version": "1.0",
                            "effective_date": "2026-01-01",
                        },
                    }
                ]
            }
        }


@pytest.mark.asyncio
async def test_retriever_embeds_query_and_maps_policy_context() -> None:
    embedding_provider = FakeEmbeddingProvider()
    client = FakeOpenSearchClient()
    retriever = OpenSearchPolicyRetriever(
        client=client,
        embedding_provider=embedding_provider,
        index_name="policies",
    )

    results = await retriever.retrieve("bank ownership", limit=5)

    assert embedding_provider.received_texts == ["bank ownership"]
    assert client.received_index == "policies"
    assert client.received_body["query"]["knn"]["embedding"]["k"] == 5
    assert len(results) == 1
    assert results[0].document_id == "policy-001"
    assert results[0].score == 0.95
