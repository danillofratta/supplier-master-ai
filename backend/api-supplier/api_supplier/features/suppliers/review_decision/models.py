from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class SupplierReviewDecisionRequest(BaseModel):
    decision: Literal["approve", "reject"]
    reason: str | None = Field(
        default=None,
        max_length=1000,
    )


class SupplierReviewDecisionResponse(BaseModel):
    workflow_id: UUID
    supplier_id: UUID
    status: str
