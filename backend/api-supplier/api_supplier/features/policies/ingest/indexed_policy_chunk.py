from dataclasses import dataclass

from api_supplier.features.policies.ingest.policy_chunk import PolicyChunk


@dataclass(frozen=True, slots=True)
class IndexedPolicyChunk:
    chunk: PolicyChunk
    embedding: tuple[float, ...]
