from dataclasses import dataclass

@dataclass(frozen=True)
class SAPSupplier:
    business_partner_id: str
    supplier_id: str