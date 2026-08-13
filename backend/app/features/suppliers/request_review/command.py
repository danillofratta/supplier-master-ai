from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class RequestSupplierReviewCommand:
    supplier_id: UUID
    risk_level: str
    reason: str
    policy_ids: tuple[str, ...]
