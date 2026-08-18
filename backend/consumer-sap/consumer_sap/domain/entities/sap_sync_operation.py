from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4
from consumer_sap.domain.enums.sap_sync_status import SapSyncStatus

@dataclass
class SapSyncOperation:
    operation_id: UUID
    message_id: UUID
    workflow_id: UUID
    supplier_id: UUID
    tax_id: str
    status: SapSyncStatus
    business_partner_id: str | None = None
    sap_supplier_id: str | None = None
    attempts: int = 0
    failure_reason: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @classmethod
    def start(cls, *, message_id: UUID, workflow_id: UUID, supplier_id: UUID, tax_id: str):
        return cls(uuid4(), message_id, workflow_id, supplier_id, tax_id, SapSyncStatus.PENDING)

    def begin(self) -> None:
        self.status = SapSyncStatus.PROCESSING
        self.attempts += 1
        self.updated_at = datetime.now(UTC)

    def complete(self, business_partner_id: str, sap_supplier_id: str | None) -> None:
        self.business_partner_id = business_partner_id
        self.sap_supplier_id = sap_supplier_id
        self.status = SapSyncStatus.COMPLETED
        self.updated_at = datetime.now(UTC)

    def fail(self, reason: str) -> None:
        self.failure_reason = reason
        self.status = SapSyncStatus.FAILED
        self.updated_at = datetime.now(UTC)
