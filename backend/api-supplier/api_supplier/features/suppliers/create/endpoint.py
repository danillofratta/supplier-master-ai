from typing import Annotated

from fastapi import APIRouter, Depends, status

from api_supplier.bootstrap.dependencies import get_create_supplier_handler
from api_supplier.features.suppliers.create.handler import CreateSupplierHandler
from api_supplier.features.suppliers.create.mapper import map_request_to_command
from api_supplier.features.suppliers.create.models import (
    CreateSupplierRequest,
    CreateSupplierResponse,
)

router = APIRouter(prefix="/v1/suppliers", tags=["Suppliers"])


@router.post(
    "/",
    response_model=CreateSupplierResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_supplier(
    request: CreateSupplierRequest,
    handler: Annotated[
        CreateSupplierHandler,
        Depends(get_create_supplier_handler),
    ],
) -> CreateSupplierResponse:
    command = map_request_to_command(request)
    supplier = await handler.handle(command)
    return CreateSupplierResponse.from_domain(supplier)
