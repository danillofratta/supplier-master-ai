from typing import Protocol
from uuid import UUID

from api_supplier.domain.entities.supplier import Supplier


class SupplierRepository(Protocol):
    async def add(
        self,
        supplier: Supplier,
    ) -> None:
        ...

    async def update(
        self,
        supplier: Supplier,
    ) -> None:
        ...

    async def get_by_id(
        self,
        supplier_id: UUID,
    ) -> Supplier | None:
        ...

    async def get_by_tax_id(
        self,
        tax_id: str,
    ) -> Supplier | None:
        ...

    async def list_all(
        self,
    ) -> tuple[Supplier, ...]:
        ...
