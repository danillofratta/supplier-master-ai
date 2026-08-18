import json
from dataclasses import asdict, dataclass
from uuid import UUID, uuid4

SAP_SYNC_COMPLETED_V1 = "supplier.sap-sync.completed.v1"

@dataclass(frozen=True, slots=True)
class AddressDto:
    street: str
    city: str
    state: str
    zip_code: str
    country: str

@dataclass(frozen=True, slots=True)
class SyncSupplierMessageDto:
    message_id: UUID
    workflow_id: UUID
    supplier_id: UUID
    name: str
    email: str
    phone: str
    tax_id: str
    address: AddressDto

@dataclass(frozen=True, slots=True)
class SapSyncCompletedDto:
    event_id: UUID
    workflow_id: UUID
    supplier_id: UUID
    business_partner_id: str
    sap_supplier_id: str | None
    version: int = 1

    @classmethod
    def create(cls, *, workflow_id, supplier_id, business_partner_id, sap_supplier_id):
        return cls(uuid4(), workflow_id, supplier_id, business_partner_id, sap_supplier_id)

    def to_json(self) -> str:
        return json.dumps(asdict(self), default=str, separators=(",", ":"))
