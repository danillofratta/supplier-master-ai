from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class SyncSupplierToSapResult:
    supplier_id: UUID
    business_partner_id: str
    sap_supplier_id: str | None
    already_existed: bool
