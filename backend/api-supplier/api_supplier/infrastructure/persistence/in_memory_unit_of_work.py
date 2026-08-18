from __future__ import annotations

from types import TracebackType
from typing import Self

from api_supplier.infrastructure.persistence.repositories.outbox_repository import (
    InMemoryOutboxRepository,
)
from api_supplier.infrastructure.persistence.repositories.supplier_onboarding_workflow_repository import (
    InMemorySupplierOnboardingWorkflowRepository,
)
from api_supplier.infrastructure.persistence.repositories.supplier_repository import (
    InMemorySupplierRepository,
)


class InMemorySupplierUnitOfWork:
    def __init__(
        self,
        repository: InMemorySupplierRepository | None = None,
        onboarding_repository: InMemorySupplierOnboardingWorkflowRepository | None = None,
        outbox_repository: InMemoryOutboxRepository | None = None,
    ) -> None:
        self.suppliers = repository or InMemorySupplierRepository()
        self.onboarding_workflows = (
            onboarding_repository
            or InMemorySupplierOnboardingWorkflowRepository()
        )
        self.outbox_messages = (
            outbox_repository
            or InMemoryOutboxRepository()
        )
        self.committed = False
        self.rolled_back = False

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if exc_type is not None:
            await self.rollback()

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        self.rolled_back = True
