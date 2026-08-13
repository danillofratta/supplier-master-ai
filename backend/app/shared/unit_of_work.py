from __future__ import annotations

from types import TracebackType
from typing import Protocol, Self

from backend.app.domain.repositories.supplier_onboarding_workflow_repository import SupplierOnboardingWorkflowRepository
from backend.app.domain.repositories.supplier_repository import SupplierRepository


class SupplierUnitOfWork(Protocol):
    suppliers: SupplierRepository
    onboarding_workflows: SupplierOnboardingWorkflowRepository

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
