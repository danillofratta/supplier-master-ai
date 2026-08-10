from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class IngestPolicyResult:
    document_id: str
    chunks_indexed: int
    embedding_dimensions: int