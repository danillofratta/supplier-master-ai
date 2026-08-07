from backend.app.domain.entities.address import Address
from backend.app.domain.entities.supplier import Supplier
from backend.app.domain.repositories.supplier_repository import SupplierRepository
from backend.app.features.suppliers.create.exceptions import (
    SupplierAlreadyExistsError,
)
from backend.app.features.suppliers.create.models import CreateSupplierCommand


class CreateSupplierHandler:
    def __init__(self, repository: SupplierRepository) -> None:
        self._repository = repository

    async def handle(self, command: CreateSupplierCommand) -> Supplier:
        existing_supplier = await self._repository.get_by_tax_id(command.tax_id)

        if existing_supplier is not None:
            raise SupplierAlreadyExistsError(command.tax_id)

        address = Address(
            street=command.address.street,
            city=command.address.city,
            state=command.address.state,
            zip_code=command.address.zip_code,
            country=command.address.country,
        )

        supplier = Supplier.create(
            name=command.name,
            email=command.email,
            phone=command.phone,
            tax_id=command.tax_id,
            address=address,
        )
        await self._repository.add(supplier)
        return supplier
