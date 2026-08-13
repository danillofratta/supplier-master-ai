from dataclasses import dataclass
from uuid import UUID

from backend.app.domain.enums.supplier_onboarding_status import (
    SupplierOnboardingStatus,
)


@dataclass(frozen=True, slots=True)
class StartSupplierOnboardingWorkflowResult:
    onboarding_workflow_id: UUID
    supplier_id: UUID
    status: SupplierOnboardingStatus
