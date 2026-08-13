from uuid import uuid4

import pytest

from backend.app.domain.entities.address import Address
from backend.app.domain.entities.supplier import Supplier
from backend.app.features.suppliers.sync_to_sap.command import (
    SyncSupplierToSapCommand,
)
from backend.app.features.suppliers.sync_to_sap.handler import (
    SyncSupplierToSapHandler,
)
from backend.app.features.suppliers.sync_to_sap.models import (
    SapSupplierDto,
)
from backend.app.infrastructure.integrations.sap.fake_sap_supplier_gateway import (
    FakeSapSupplierGateway,
)
from backend.app.infrastructure.persistence.repositories.supplier_repository import (
    InMemorySupplierRepository,
)


class InMemorySupplierUnitOfWork:
    def __init__(
        self,
        repository: InMemorySupplierRepository,
    ) -> None:
        self.suppliers = repository
        self.committed = False
        self.rolled_back = False

    async def __aenter__(self):
        return self

    async def __aexit__(
        self,
        exc_type,
        exc,
        traceback,
    ) -> None:
        if exc is not None:
            await self.rollback()

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        self.rolled_back = True


def build_supplier() -> Supplier:
    return Supplier(
        supplier_id=uuid4(),
        name="ACME Supplies",
        email="contact@acme.com",
        phone="11999999999",
        tax_id="12.345.678/0001-90",
        address=Address(
            street="Main Street",
            city="Sao Paulo",
            state="SP",
            zip_code="01000-000",
            country="Brazil",
        ),
    )


@pytest.mark.asyncio
async def test_existing_supplier_in_sap_is_not_created_again() -> None:
    supplier = build_supplier()
    repository = InMemorySupplierRepository()
    await repository.add(supplier)

    uow = InMemorySupplierUnitOfWork(repository)
    sap_gateway = FakeSapSupplierGateway()
    sap_gateway.seed(
        tax_id=supplier.tax_id,
        reference=SapSupplierDto(
            business_partner_id="100000777",
            supplier_id="200000777",
        ),
    )

    handler = SyncSupplierToSapHandler(
        unit_of_work=uow,
        sap_gateway=sap_gateway,
    )

    result = await handler.handle(
        SyncSupplierToSapCommand(
            supplier_id=supplier.supplier_id,
        )
    )

    assert result.already_existed is True
    assert result.business_partner_id == "100000777"
    assert result.sap_supplier_id == "200000777"
    assert sap_gateway.created_suppliers == []


@pytest.mark.asyncio
async def test_new_supplier_is_created_in_sap() -> None:
    supplier = build_supplier()
    repository = InMemorySupplierRepository()
    await repository.add(supplier)

    uow = InMemorySupplierUnitOfWork(repository)
    sap_gateway = FakeSapSupplierGateway()

    handler = SyncSupplierToSapHandler(
        unit_of_work=uow,
        sap_gateway=sap_gateway,
    )

    result = await handler.handle(
        SyncSupplierToSapCommand(
            supplier_id=supplier.supplier_id,
        )
    )

    assert result.already_existed is False
    assert result.business_partner_id == "100000001"
    assert result.sap_supplier_id == "200000001"
    assert sap_gateway.created_suppliers == [supplier]
