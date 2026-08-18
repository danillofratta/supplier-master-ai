from typing import Protocol
from uuid import UUID
from consumer_supplier_sap_result.domain.entities.workflow import SupplierOnboardingWorkflow

class WorkflowRepository(Protocol):
    async def get_by_id(self, workflow_id: UUID) -> SupplierOnboardingWorkflow | None: ...
    async def update(self, workflow: SupplierOnboardingWorkflow) -> None: ...
