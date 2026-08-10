from dataclasses import dataclass
from typing import Protocol

from backend.app.features.policies.ingest.command import IngestPolicyCommand
from backend.app.features.policies.ingest.policy_chunk import PolicyChunk


@dataclass(frozen=True, slots=True)
class DocumentChunker(Protocol):
    def split(
            self,
            command: IngestPolicyCommand    
    ) -> tuple[PolicyChunk, ...]:
        ...