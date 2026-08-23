from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class SupplierResponse(BaseModel):
    supplier_id: UUID = Field(
        description="Unique supplier identifier."
    )

    name: str = Field(
        description="Supplier legal or business name."
    )

    email: str
    phone: str
    tax_id: str

    status: str = Field(
        description="Current supplier status."
    )

    street: str
    city: str
    state: str
    zip_code: str
    country: str

class SupplierListItem(BaseModel):
    supplier_id: UUID
    name: str
    email: str
    tax_id: str
    status: str    

class SupplierListResponse(BaseModel):
    items: list[SupplierListItem]    

from pydantic import BaseModel, Field


class SupplierAnalysisResponse(BaseModel):
    risk_level: str

    recommended_action: str

    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )

    missing_documents: list[str]

    policy_violations: list[str]

    summary: str

class OnboardingStatusResponse(BaseModel):
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

class StartOnboardingResponse(BaseModel):
    onboarding_workflow_id: UUID
    supplier_id: UUID
    status: str    