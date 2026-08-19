from api_supplier.features.suppliers.get_by_id.query import (
    GetSupplierByIdQuery,
)
from api_supplier.features.suppliers.get_by_id.result import (
    GetSupplierByIdResult,
)
from api_supplier.shared.unit_of_work import (
    SupplierUnitOfWork,
)


class GetSupplierByIdHandler:
    def __init__(
        self,
        unit_of_work: SupplierUnitOfWork,
    ) -> None:
        self._unit_of_work = unit_of_work

    async def handle(
        self,
        query: GetSupplierByIdQuery,
    ) -> GetSupplierByIdResult | None:
        async with self._unit_of_work as uow:
            supplier = await uow.suppliers.get_by_id(
                query.supplier_id
            )

        if supplier is None:
            return None

        return GetSupplierByIdResult(
            supplier_id=supplier.supplier_id,
            name=supplier.name,
            email=supplier.email,
            phone=supplier.phone,
            tax_id=supplier.tax_id,
            status=supplier.status.value,
            street=supplier.address.street,
            city=supplier.address.city,
            state=supplier.address.state,
            zip_code=supplier.address.zip_code,
            country=supplier.address.country,
        )
