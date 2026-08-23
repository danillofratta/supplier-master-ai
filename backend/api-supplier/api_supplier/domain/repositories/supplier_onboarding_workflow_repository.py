from typing import Protocol
from uuid import UUID

from api_supplier.domain.entities.supplier_onboarding_workflow import (
    SupplierOnboardingWorkflow,
)


class SupplierOnboardingWorkflowWriteConflictError(Exception):
    """Raised when a concurrent workflow insert violates a DB constraint."""


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

    async def get_by_idempotency_key(
        self,
        idempotency_key: UUID,
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
