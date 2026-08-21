from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from api_supplier.bootstrap.dependencies import get_start_supplier_onboarding_handler
from api_supplier.features.suppliers.onboarding_workflow.command import StartSupplierOnboardingWorkflowCommand
from api_supplier.features.suppliers.onboarding_workflow.handler import StartSupplierOnboardingWorkflowHandler
from api_supplier.features.suppliers.onboarding_workflow.models import StartSupplierOnboardingResponse

router = APIRouter(prefix="/v1/suppliers", tags=["Suppliers"])


@router.post(
    "/{supplier_id}/onboarding",
    response_model=StartSupplierOnboardingResponse,
    status_code=status.HTTP_201_CREATED,
)
async def start_supplier_onboarding(
    supplier_id: UUID,
    handler: Annotated[StartSupplierOnboardingWorkflowHandler, Depends(get_start_supplier_onboarding_handler)],
) -> StartSupplierOnboardingResponse:
    result = await handler.handle(StartSupplierOnboardingWorkflowCommand(supplier_id=supplier_id))
    return StartSupplierOnboardingResponse(
        onboarding_workflow_id=result.onboarding_workflow_id,
        supplier_id=result.supplier_id,
        status=result.status.value,
    )
