from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class SupplierReviewRequestDto:
    supplier_id: UUID
    supplier_name: str
    tax_id: str
    risk_level: str
    reason: str
    policy_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ServiceNowTicketDto:
    ticket_id: str
    ticket_number: str
    status: str
