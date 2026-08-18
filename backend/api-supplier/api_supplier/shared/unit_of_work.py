from __future__ import annotations

from types import TracebackType
from typing import Protocol, Self

from api_supplier.domain.repositories.outbox_repository import OutboxRepository
from api_supplier.domain.repositories.supplier_onboarding_workflow_repository import (
    SupplierOnboardingWorkflowRepository,
)
from api_supplier.domain.repositories.supplier_repository import SupplierRepository


class SupplierUnitOfWork(Protocol):
    suppliers: SupplierRepository
    onboarding_workflows: SupplierOnboardingWorkflowRepository
    outbox_messages: OutboxRepository

    async def __aenter__(self) -> Self:
        ...

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        ...

    async def commit(self) -> None:
        ...

    async def rollback(self) -> None:
        ...
