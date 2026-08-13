from __future__ import annotations

import asyncio
from typing import Any

from backend.app.features.policies.ingest.embedding_provider import EmbeddingProvider
from backend.app.features.suppliers.analyze.policy_context import PolicyContext


class OpenSearchPolicyRetriever:
    def __init__(
        self,
        *,
        client: Any,
        embedding_provider: EmbeddingProvider,
        index_name: str,
    ) -> None:
        self._client = client
        self._embedding_provider = embedding_provider
        self._index_name = index_name

    async def retrieve(
        self,
        query: str,
        *,
        limit: int = 5,
    ) -> tuple[PolicyContext, ...]:
        if not query.strip():
            return ()
        if limit <= 0:
            raise ValueError("limit must be greater than zero.")

        query_embedding = await self._embedding_provider.generate(query)
        response = await asyncio.to_thread(
            self._search_sync,
            query_embedding,
            limit,
        )
        return self._map_results(response)

    def _search_sync(
        self,
        query_embedding: tuple[float, ...],
        limit: int,
    ) -> dict:
        return self._client.search(
            index=self._index_name,
            body={
                "size": limit,
                "_source": {
                    "excludes": ["embedding"],
                },
                "query": {
                    "knn": {
                        "embedding": {
                            "vector": list(query_embedding),
                            "k": limit,
                        }
                    }
                },
            },
        )

    @staticmethod
    def _map_results(response: dict) -> tuple[PolicyContext, ...]:
        hits = response.get("hits", {}).get("hits", [])
        contexts: list[PolicyContext] = []

        for hit in hits:
            source = hit.get("_source", {})
            contexts.append(
                PolicyContext(
                    document_id=str(source["document_id"]),
                    chunk_id=str(source["chunk_id"]),
                    title=str(source["title"]),
                    content=str(source["content"]),
                    policy_type=str(source["policy_type"]),
                    version=str(source["version"]),
                    effective_date=str(source["effective_date"]),
                    score=float(hit.get("_score", 0.0)),
                )
            )

        return tuple(contexts)
