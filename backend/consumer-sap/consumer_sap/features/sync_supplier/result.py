from dataclasses import dataclass
@dataclass(frozen=True, slots=True)
class SyncSupplierResult:
    business_partner_id: str
    sap_supplier_id: str | None
    already_existed: bool
