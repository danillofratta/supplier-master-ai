from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class RequestSupplierReviewResult:
    supplier_id: UUID
    ticket_id: str
    ticket_number: str
    status: str
