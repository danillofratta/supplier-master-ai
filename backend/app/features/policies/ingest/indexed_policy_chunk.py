from attr import dataclass

from backend.app.features.policies.ingest.police_chunk import PolicyChunk


@dataclass(frozen=True, slots=True)
class IndexedPolicyChunk:
    chunk: PolicyChunk
    embedding: tuple[float]