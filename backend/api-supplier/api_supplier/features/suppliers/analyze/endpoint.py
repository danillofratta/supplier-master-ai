from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from api_supplier.bootstrap.dependencies import get_analyze_supplier_handler
from api_supplier.features.suppliers.analyze.command import AnalyzeSupplierCommand
from api_supplier.features.suppliers.analyze.handler import AnalyzeSupplierHandler
from api_supplier.features.suppliers.analyze.models import AnalyzeSupplierResponse

router = APIRouter(prefix="/v1/suppliers", tags=["Suppliers"])


@router.post(
    "/{supplier_id}/analysis",
    response_model=AnalyzeSupplierResponse,
    status_code=status.HTTP_200_OK,
)
async def analyze_supplier(
    supplier_id: UUID,
    handler: Annotated[
        AnalyzeSupplierHandler,
        Depends(get_analyze_supplier_handler),
    ],
) -> AnalyzeSupplierResponse:
    result = await handler.handle(
        AnalyzeSupplierCommand(supplier_id=supplier_id)
    )
    return AnalyzeSupplierResponse.from_result(result)
