from backend.app.domain.entities.supplier import Supplier
from backend.app.features.suppliers.sync_to_sap.models import (
    SapSupplierDto
)


class FakeSapSupplierGateway:
    def __init__(self) -> None:
        self._suppliers: dict[str, SapSupplierDto] = {}
        self.created_suppliers: list[Supplier] = []

    async def find_by_tax_id(
        self,
        tax_id: str,
    ) -> SapSupplierDto | None:
        return self._suppliers.get(
            self._normalize_tax_id(tax_id)
        )

    async def create_supplier(
        self,
        supplier: Supplier,
    ) -> SapSupplierDto:
        reference = SapSupplierDto(
            business_partner_id="100000001",
            supplier_id="200000001",
        )

        self._suppliers[
            self._normalize_tax_id(supplier.tax_id)
        ] = reference
        self.created_suppliers.append(supplier)

        return reference

    def seed(
        self,
        *,
        tax_id: str,
        reference: SapSupplierDto,
    ) -> None:
        self._suppliers[
            self._normalize_tax_id(tax_id)
        ] = reference

    @staticmethod
    def _normalize_tax_id(tax_id: str) -> str:
        return "".join(
            character.lower()
            for character in tax_id
            if character.isalnum()
        )
