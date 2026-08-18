from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class FailSapSyncCommand:
    message_id: UUID
    workflow_id: UUID
    supplier_id: UUID
    reason: str
