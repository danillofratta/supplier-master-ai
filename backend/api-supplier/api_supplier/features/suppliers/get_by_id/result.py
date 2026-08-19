from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class GetSupplierByIdResult:
    supplier_id: UUID
    name: str
    email: str
    phone: str
    tax_id: str
    status: str
    street: str
    city: str
    state: str
    zip_code: str
    country: str
