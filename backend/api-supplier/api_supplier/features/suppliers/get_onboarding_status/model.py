from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class SupplierOnboardingResponse(BaseModel):
    workflow_id: UUID
    correlation_id: UUID
    supplier_id: UUID
    status: str
    service_now_ticket_id: str | None
    sap_business_partner_id: str | None
    rejection_reason: str | None
    failure_reason: str | None
    created_at: datetime
    updated_at: datetime
