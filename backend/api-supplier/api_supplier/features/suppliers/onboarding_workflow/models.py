from uuid import UUID
from pydantic import BaseModel


class StartSupplierOnboardingResponse(BaseModel):
    onboarding_workflow_id: UUID
    supplier_id: UUID
    status: str
