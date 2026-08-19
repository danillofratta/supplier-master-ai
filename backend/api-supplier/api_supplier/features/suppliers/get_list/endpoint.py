from typing import Annotated

from fastapi import APIRouter, Depends

from api_supplier.bootstrap.dependencies import (
    get_list_suppliers_handler,
)
from api_supplier.features.suppliers.get_list.handler import (
    ListSuppliersHandler,
)
from api_supplier.features.suppliers.get_list.model import (
    ListSuppliersResponse,
    SupplierListItemResponse,
)
from api_supplier.features.suppliers.get_list.query import (
    ListSuppliersQuery,
)


router = APIRouter(
    prefix="/v1/suppliers",
    tags=["Suppliers"],
)


@router.get(
    "",
    response_model=ListSuppliersResponse,
)
async def list_suppliers(
    handler: Annotated[
        ListSuppliersHandler,
        Depends(get_list_suppliers_handler),
    ],
) -> ListSuppliersResponse:
    result = await handler.handle(
        ListSuppliersQuery()
    )

    return ListSuppliersResponse(
        items=[
            SupplierListItemResponse(
                supplier_id=item.supplier_id,
                name=item.name,
                email=item.email,
                tax_id=item.tax_id,
                status=item.status,
            )
            for item in result.items
        ]
    )
