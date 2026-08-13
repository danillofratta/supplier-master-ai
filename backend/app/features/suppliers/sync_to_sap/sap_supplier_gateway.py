from typing import Protocol

from backend.app.domain.entities.supplier import Supplier
from backend.app.features.suppliers.sync_to_sap.models import (
    SapSupplierDto,
)


class SapSupplierGateway(Protocol):
    async def find_by_tax_id(
        self,
        tax_id: str,
    ) -> SapSupplierDto | None:
        ...

    async def create_supplier(
        self,
        supplier: Supplier,
    ) -> SapSupplierDto:
        ...
