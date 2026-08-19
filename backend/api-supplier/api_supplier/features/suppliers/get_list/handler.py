from api_supplier.features.suppliers.get_list.query import (
    ListSuppliersQuery,
)
from api_supplier.features.suppliers.get_list.result import (
    ListSuppliersResult,
    SupplierListItemResult,
)
from api_supplier.shared.unit_of_work import (
    SupplierUnitOfWork,
)


class ListSuppliersHandler:
    def __init__(
        self,
        unit_of_work: SupplierUnitOfWork,
    ) -> None:
        self._unit_of_work = unit_of_work

    async def handle(
        self,
        query: ListSuppliersQuery,
    ) -> ListSuppliersResult:
        async with self._unit_of_work as uow:
            suppliers = await uow.suppliers.list_all()

        return ListSuppliersResult(
            items=tuple(
                SupplierListItemResult(
                    supplier_id=supplier.supplier_id,
                    name=supplier.name,
                    email=supplier.email,
                    tax_id=supplier.tax_id,
                    status=supplier.status.value,
                )
                for supplier in suppliers
            )
        )
