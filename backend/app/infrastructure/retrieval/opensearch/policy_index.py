from __future__ import annotations

import asyncio
from typing import Any

from backend.app.features.policies.ingest.indexed_policy_chunk import (
    IndexedPolicyChunk,
)
from backend.app.infrastructure.retrieval.opensearch.index_mapping import (
    build_policy_index_mapping,
)


class OpenSearchPolicyIndexInitializer:
    def __init__(
        self,
        client: Any,
        *,
        index_name: str,
        dimensions: int,
    ) -> None:
        self._client = client
        self._index_name = index_name
        self._dimensions = dimensions

    async def ensure_exists(self) -> None:
        await asyncio.to_thread(self._ensure_exists_sync)

    def _ensure_exists_sync(self) -> None:
        if self._client.indices.exists(index=self._index_name):
            return

        self._client.indices.create(
            index=self._index_name,
            body=build_policy_index_mapping(dimensions=self._dimensions),
        )


class OpenSearchPolicyIndex:
    def __init__(
        self,
        client: Any,
        *,
        index_name: str,
    ) -> None:
        self._client = client
        self._index_name = index_name

    async def delete_document(
        self,
        document_id: str,
        version: str,
    ) -> None:
        await asyncio.to_thread(
            self._delete_document_sync,
            document_id,
            version,
        )

    def _delete_document_sync(
        self,
        document_id: str,
        version: str,
    ) -> None:
        response = self._client.search(
            index=self._index_name,
            body={
                "_source": False,
                "size": 1000,
                "query": {
                    "bool": {
                        "filter": [
                            {
                                "term": {
                                    "document_id": document_id,
                                }
                            },
                            {
                                "term": {
                                    "version": version,
                                }
                            },
                        ]
                    }
                },
            },
        )

        hits = response.get("hits", {}).get("hits", [])

        for hit in hits:
            self._client.delete(
                index=self._index_name,
                id=hit["_id"],
                refresh=False,
            )

    async def upsert(
        self,
        chunks: tuple[IndexedPolicyChunk, ...],
    ) -> None:
        await asyncio.to_thread(
            self._upsert_sync,
            chunks,
        )

    def _upsert_sync(
        self,
        chunks: tuple[IndexedPolicyChunk, ...],
    ) -> None:
        for indexed_chunk in chunks:
            chunk = indexed_chunk.chunk

            document = {
                "document_id": chunk.document_id,
                "chunk_id": chunk.chunk_id,
                "title": chunk.title,
                "content": chunk.content,
                "policy_type": chunk.policy_type,
                "version": chunk.version,
                "effective_date": chunk.effective_date,
                "position": chunk.position,
                "embedding": list(indexed_chunk.embedding),
            }

            self._client.index(
                index=self._index_name,
                id=chunk.chunk_id,
                body=document
            )
