from uuid import UUID

from backend.app.domain.entities.supplier import Supplier


class InMemorySupplierRepository:
    def __init__(self) -> None:
        self._suppliers: dict[UUID, Supplier] = {}

    async def add(self, supplier: Supplier) -> None:
        self._suppliers[supplier.supplier_id] = supplier

    async def update(self, supplier: Supplier) -> None:
        self._suppliers[supplier.supplier_id] = supplier

    async def get_by_id(self, supplier_id: UUID) -> Supplier | None:
        return self._suppliers.get(supplier_id)

    async def get_all(self) -> list[Supplier]:
        return list(self._suppliers.values())

    async def get_by_tax_id(self, tax_id: str) -> Supplier | None:
        normalized_tax_id = self._normalize_tax_id(tax_id)
        return next(
            (
                supplier
                for supplier in self._suppliers.values()
                if self._normalize_tax_id(supplier.tax_id) == normalized_tax_id
            ),
            None,
        )

    @staticmethod
    def _normalize_tax_id(tax_id: str) -> str:
        return "".join(
            character.lower()
            for character in tax_id
            if character.isalnum()
        )
