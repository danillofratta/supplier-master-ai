from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from api_supplier.bootstrap.dependencies import get_decide_supplier_review_handler
from api_supplier.features.suppliers.review_decision.command import DecideSupplierReviewCommand
from api_supplier.features.suppliers.review_decision.handler import DecideSupplierReviewHandler
from api_supplier.features.suppliers.review_decision.models import SupplierReviewDecisionRequest, SupplierReviewDecisionResponse

router = APIRouter(prefix="/v1/suppliers", tags=["Suppliers"])


@router.post("/{supplier_id}/onboarding/review-decision", response_model=SupplierReviewDecisionResponse)
async def decide_supplier_review(
    supplier_id: UUID,
    request: SupplierReviewDecisionRequest,
    handler: Annotated[DecideSupplierReviewHandler, Depends(get_decide_supplier_review_handler)],
) -> SupplierReviewDecisionResponse:
    try:
        workflow = await handler.handle(
            DecideSupplierReviewCommand(
                supplier_id=supplier_id,
                decision=request.decision,
                reason=request.reason,
            )
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    return SupplierReviewDecisionResponse(
        workflow_id=workflow.workflow_id,
        supplier_id=workflow.supplier_id,
        status=workflow.status.value,
    )
