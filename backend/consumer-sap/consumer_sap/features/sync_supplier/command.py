from dataclasses import dataclass
from uuid import UUID

from consumer_sap.features.sync_supplier.contracts import AddressDto


@dataclass(frozen=True, slots=True)
class SyncSupplierCommand:
    message_id: UUID
    correlation_id: UUID
    workflow_id: UUID
    supplier_id: UUID
    name: str
    email: str
    phone: str
    tax_id: str
    address: AddressDto
