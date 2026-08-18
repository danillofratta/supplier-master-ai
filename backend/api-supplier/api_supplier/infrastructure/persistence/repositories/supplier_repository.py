from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api_supplier.domain.entities.supplier import Supplier
from api_supplier.infrastructure.persistence.sqlalchemy.mappers.supplier_mapper import (
    SupplierMapper,
)
from api_supplier.infrastructure.persistence.sqlalchemy.models.supplier_model import (
    SupplierModel,
)


class PostgreSQLSupplierRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, supplier: Supplier) -> None:
        self._session.add(SupplierMapper.to_model(supplier))

    async def update(self, supplier: Supplier) -> None:
        model = await self._session.get(SupplierModel, supplier.supplier_id)
        if model is None:
            self._session.add(SupplierMapper.to_model(supplier))
            return

        model.name = supplier.name
        model.email = supplier.email
        model.phone = supplier.phone
        model.tax_id = supplier.tax_id
        model.normalized_tax_id = SupplierMapper.normalize_tax_id(supplier.tax_id)
        model.status = supplier.status.value
        model.street = supplier.address.street
        model.city = supplier.address.city
        model.state = supplier.address.state
        model.zip_code = supplier.address.zip_code
        model.country = supplier.address.country
        model.updated_at = supplier.updated_at

    async def get_by_id(self, supplier_id: UUID) -> Supplier | None:
        model = await self._session.get(SupplierModel, supplier_id)
        return None if model is None else SupplierMapper.to_domain(model)

    async def get_all(self) -> list[Supplier]:
        result = await self._session.execute(select(SupplierModel))
        return [SupplierMapper.to_domain(model) for model in result.scalars().all()]

    async def get_by_tax_id(self, tax_id: str) -> Supplier | None:
        normalized_tax_id = SupplierMapper.normalize_tax_id(tax_id)
        result = await self._session.execute(
            select(SupplierModel).where(
                SupplierModel.normalized_tax_id == normalized_tax_id
            )
        )
        model = result.scalar_one_or_none()
        return None if model is None else SupplierMapper.to_domain(model)


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
