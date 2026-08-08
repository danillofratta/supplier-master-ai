from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class AnalyzeSupplierCommand:
    supplier_id: UUID
