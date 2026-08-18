from api_supplier.domain.entities.address import Address
from api_supplier.domain.entities.supplier import Supplier
from api_supplier.features.suppliers.create.exceptions import (
    SupplierAlreadyExistsError,
)
from api_supplier.features.suppliers.create.models import CreateSupplierCommand
from api_supplier.shared.unit_of_work import SupplierUnitOfWork


class CreateSupplierHandler:
    def __init__(self, unit_of_work: SupplierUnitOfWork) -> None:
        self._unit_of_work = unit_of_work

    async def handle(self, command: CreateSupplierCommand) -> Supplier:
        async with self._unit_of_work as uow:
            existing_supplier = await uow.suppliers.get_by_tax_id(command.tax_id)

            if existing_supplier is not None:
                raise SupplierAlreadyExistsError(command.tax_id)

            supplier = Supplier.create(
                name=command.name,
                email=command.email,
                phone=command.phone,
                tax_id=command.tax_id,
                address=Address(
                    street=command.address.street,
                    city=command.address.city,
                    state=command.address.state,
                    zip_code=command.address.zip_code,
                    country=command.address.country,
                ),
            )

            await uow.suppliers.add(supplier)
            await uow.commit()

            return supplier
