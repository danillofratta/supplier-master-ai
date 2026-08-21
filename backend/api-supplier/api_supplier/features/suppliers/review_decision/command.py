from dataclasses import dataclass
from typing import Literal
from uuid import UUID


@dataclass(frozen=True, slots=True)
class DecideSupplierReviewCommand:
    supplier_id: UUID
    decision: Literal["approve", "reject"]
    reason: str | None = None
