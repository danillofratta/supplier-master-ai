from __future__ import annotations

from types import TracebackType
from typing import Self

from backend.app.infrastructure.persistence.repositories.supplier_repository import (
    InMemorySupplierRepository,
)


class InMemorySupplierUnitOfWork:
    def __init__(
        self,
        repository: InMemorySupplierRepository | None = None,
    ) -> None:
        self.suppliers = repository or InMemorySupplierRepository()
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
