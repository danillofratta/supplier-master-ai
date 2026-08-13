from __future__ import annotations

from types import TracebackType
from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from backend.app.infrastructure.persistence.repositories.supplier_onboarding_workflow_repository import (
    PostgreSQLSupplierOnboardingWorkflowRepository,
)
from backend.app.infrastructure.persistence.repositories.supplier_repository import (
    PostgreSQLSupplierRepository,
)


class SqlAlchemySupplierUnitOfWork:
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        self._session_factory = session_factory
        self._session: AsyncSession | None = None
        self.suppliers: PostgreSQLSupplierRepository
        self.onboarding_workflows: PostgreSQLSupplierOnboardingWorkflowRepository

    async def __aenter__(self) -> Self:
        self._session = self._session_factory()
        self.suppliers = PostgreSQLSupplierRepository(self._session)
        self.onboarding_workflows = (
            PostgreSQLSupplierOnboardingWorkflowRepository(
                self._session
            )
        )
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if self._session is None:
            return

        try:
            if exc_type is not None:
                await self.rollback()
        finally:
            await self._session.close()
            self._session = None

    async def commit(self) -> None:
        if self._session is None:
            raise RuntimeError("Unit of Work is not active.")
        await self._session.commit()

    async def rollback(self) -> None:
        if self._session is None:
            raise RuntimeError("Unit of Work is not active.")
        await self._session.rollback()
