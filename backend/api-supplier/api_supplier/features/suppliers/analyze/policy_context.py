from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PolicyContext:
    document_id: str
    chunk_id: str
    title: str
    content: str
    policy_type: str
    version: str
    effective_date: str
    score: float
