from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class CompleteSapSyncCommand:
    message_id: UUID
    correlation_id: UUID
    workflow_id: UUID
    supplier_id: UUID
    business_partner_id: str
    sap_supplier_id: str | None = None
