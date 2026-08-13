from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SapSupplierDto:
    business_partner_id: str
    supplier_id: str | None = None
