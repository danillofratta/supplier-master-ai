import pytest

from backend.app.features.suppliers.create.handler import CreateSupplierHandler
from backend.app.features.suppliers.create.models import CreateSupplierAddressCommand, CreateSupplierCommand
from backend.app.features.suppliers.create.exceptions import SupplierAlreadyExistsError
from backend.app.infrastructure.supplier_repository import InMemorySupplierRepository

@pytest.mark.asyncio
async def test_should_not_create_duplicate_supplier() -> None:
    repositoy = InMemorySupplierRepository()
    handler = CreateSupplierHandler(repositoy)

    command  = CreateSupplierCommand(
            tax_id="12345",
            name="Supplier A",
            email="1@1.com",
            phone="123456789",            
            address=CreateSupplierAddressCommand(
                street="Street 1",
                city="City 1",
                state="State 1",
                zip_code="12345",
                country="Country 1"
            )   
    )

    await handler.handle(command)

    duplicate_command = CreateSupplierCommand(
            tax_id="12345",
            name="Supplier A",
            email="1@1.com",
            phone="123456789",
            address=CreateSupplierAddressCommand(
                street="Street 1",
                city="City 1",
                state="State 1",
                zip_code="12345",
                country="Country 1"
            )   
    )

    with pytest.raises(SupplierAlreadyExistsError):
        await handler.handle(duplicate_command)