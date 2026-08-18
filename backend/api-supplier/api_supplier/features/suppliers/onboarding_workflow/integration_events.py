import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid4

from api_supplier.domain.entities.supplier import Supplier


SAP_SYNC_REQUESTED_V1 = "supplier.sap-sync.requested.v1"


@dataclass(frozen=True, slots=True)
class SupplierAddressIntegrationDto:
    street: str
    city: str
    state: str
    zip_code: str
    country: str


@dataclass(frozen=True, slots=True)
class SapSyncRequestedV1:
    event_id: UUID
    workflow_id: UUID
    supplier_id: UUID
    name: str
    email: str
    phone: str
    tax_id: str
    address: SupplierAddressIntegrationDto
    occurred_at: str
    version: int = 1

    @classmethod
    def from_supplier(
        cls,
        *,
        workflow_id: UUID,
        supplier: Supplier,
    ) -> "SapSyncRequestedV1":
        return cls(
            event_id=uuid4(),
            workflow_id=workflow_id,
            supplier_id=supplier.supplier_id,
            name=supplier.name,
            email=supplier.email,
            phone=supplier.phone,
            tax_id=supplier.tax_id,
            address=SupplierAddressIntegrationDto(
                street=supplier.address.street,
                city=supplier.address.city,
                state=supplier.address.state,
                zip_code=supplier.address.zip_code,
                country=supplier.address.country,
            ),
            occurred_at=datetime.now(UTC).isoformat(),
        )

    def to_json(self) -> str:
        return json.dumps(
            asdict(self),
            default=str,
            separators=(",", ":"),
        )
