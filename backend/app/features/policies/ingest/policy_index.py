from typing import Protocol

from backend.app.features.policies.ingest.indexed_policy_chunk import (
    IndexedPolicyChunk,
)


class PolicyIndex(Protocol):
    async def upsert(
        self,
        chunks: tuple[IndexedPolicyChunk, ...],
    ) -> None:
        ...
