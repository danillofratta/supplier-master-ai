from dataclasses import dataclass
from typing import Protocol
from consumer_sap.features.sync_supplier.command import SyncSupplierCommand

@dataclass(frozen=True, slots=True)
class SapSupplierDto:
    business_partner_id: str
    supplier_id: str | None

class SapGateway(Protocol):
    async def find_by_tax_id(self, tax_id: str) -> SapSupplierDto | None: ...
    async def create_supplier(self, supplier: SyncSupplierCommand) -> SapSupplierDto: ...
