from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from api_supplier.bootstrap.dependencies import (
    get_supplier_by_id_handler,
)
from api_supplier.features.suppliers.get_by_id.handler import (
    GetSupplierByIdHandler,
)
from api_supplier.features.suppliers.get_by_id.model import (
    GetSupplierByIdResponse,
)
from api_supplier.features.suppliers.get_by_id.query import (
    GetSupplierByIdQuery,
)


router = APIRouter(
    prefix="/v1/suppliers",
    tags=["Suppliers"],
)


@router.get(
    "/{supplier_id}",
    response_model=GetSupplierByIdResponse,
)
async def get_supplier_by_id(
    supplier_id: UUID,
    handler: Annotated[
        GetSupplierByIdHandler,
        Depends(get_supplier_by_id_handler),
    ],
) -> GetSupplierByIdResponse:
    result = await handler.handle(
        GetSupplierByIdQuery(
            supplier_id=supplier_id
        )
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Supplier not found.",
        )

    return GetSupplierByIdResponse(
        supplier_id=result.supplier_id,
        name=result.name,
        email=result.email,
        phone=result.phone,
        tax_id=result.tax_id,
        status=result.status,
        street=result.street,
        city=result.city,
        state=result.state,
        zip_code=result.zip_code,
        country=result.country,
    )
