from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from api_supplier.bootstrap.dependencies import (
    get_supplier_onboarding_handler,
)
from api_supplier.features.suppliers.get_onboarding_status.handler import (
    GetSupplierOnboardingHandler,
)
from api_supplier.features.suppliers.get_onboarding_status.model import (
    SupplierOnboardingResponse,
)
from api_supplier.features.suppliers.get_onboarding_status.query import (
    GetSupplierOnboardingQuery,
)


router = APIRouter(
    prefix="/v1/suppliers",
    tags=["Suppliers"],
)


@router.get(
    "/{supplier_id}/onboarding",
    response_model=SupplierOnboardingResponse,
)
async def get_supplier_onboarding_status(
    supplier_id: UUID,
    handler: Annotated[
        GetSupplierOnboardingHandler,
        Depends(get_supplier_onboarding_handler),
    ],
) -> SupplierOnboardingResponse:
    result = await handler.handle(
        GetSupplierOnboardingQuery(
            supplier_id=supplier_id
        )
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Supplier onboarding not found.",
        )

    return SupplierOnboardingResponse(
        workflow_id=result.workflow_id,
        correlation_id=result.correlation_id,
        supplier_id=result.supplier_id,
        status=result.status,
        service_now_ticket_id=(
            result.service_now_ticket_id
        ),
        sap_business_partner_id=(
            result.sap_business_partner_id
        ),
        rejection_reason=result.rejection_reason,
        failure_reason=result.failure_reason,
        created_at=result.created_at,
        updated_at=result.updated_at,
    )
