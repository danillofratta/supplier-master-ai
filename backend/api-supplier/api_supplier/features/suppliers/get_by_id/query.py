from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class GetSupplierByIdQuery:
    supplier_id: UUID