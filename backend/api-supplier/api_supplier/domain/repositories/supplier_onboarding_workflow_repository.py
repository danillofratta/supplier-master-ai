from typing import Protocol
from uuid import UUID

from api_supplier.domain.entities.supplier_onboarding_workflow import (
    SupplierOnboardingWorkflow,
)


class SupplierOnboardingWorkflowRepository(Protocol):
    async def add(
        self,
        workflow: SupplierOnboardingWorkflow,
    ) -> None:
        ...

    async def get_by_id(
        self,
        workflow_id: UUID,
    ) -> SupplierOnboardingWorkflow | None:
        ...

    async def update(
        self,
        workflow: SupplierOnboardingWorkflow,
    ) -> None:
        ...

    async def get_latest_by_supplier_id(
        self,
        supplier_id: UUID,
    ) -> SupplierOnboardingWorkflow | None:
        ...        
