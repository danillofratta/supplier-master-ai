from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class SupplierListItemResult:
    supplier_id: UUID
    name: str
    email: str
    tax_id: str
    status: str


@dataclass(frozen=True, slots=True)
class ListSuppliersResult:
    items: tuple[SupplierListItemResult, ...]
