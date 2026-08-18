import pytest

from api_supplier.features.suppliers.create.exceptions import (
    SupplierAlreadyExistsError,
)
from api_supplier.features.suppliers.create.handler import CreateSupplierHandler
from api_supplier.features.suppliers.create.models import (
    CreateSupplierAddressCommand,
    CreateSupplierCommand,
)
from api_supplier.infrastructure.persistence.in_memory_unit_of_work import (
    InMemorySupplierUnitOfWork,
)


def build_command(tax_id: str = "12345") -> CreateSupplierCommand:
    return CreateSupplierCommand(
        tax_id=tax_id,
        name="Supplier A",
        email="1@1.com",
        phone="123456789",
        address=CreateSupplierAddressCommand(
            street="Street 1",
            city="City 1",
            state="State 1",
            zip_code="12345",
            country="Country 1",
        ),
    )


@pytest.mark.asyncio
async def test_create_supplier_commits_unit_of_work() -> None:
    uow = InMemorySupplierUnitOfWork()
    handler = CreateSupplierHandler(uow)

    supplier = await handler.handle(build_command())

    assert uow.committed is True
    assert await uow.suppliers.get_by_id(supplier.supplier_id) is supplier


@pytest.mark.asyncio
async def test_should_not_create_duplicate_supplier() -> None:
    uow = InMemorySupplierUnitOfWork()
    handler = CreateSupplierHandler(uow)

    await handler.handle(build_command("12345"))

    with pytest.raises(SupplierAlreadyExistsError):
        await handler.handle(build_command("12345"))
