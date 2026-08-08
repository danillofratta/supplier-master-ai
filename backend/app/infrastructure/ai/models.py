from pydantic import BaseModel, Field

from backend.app.domain.enums.supplier_recommended_action import (
    SupplierRecommendedAction,
)
from backend.app.domain.enums.supplier_risk_level import SupplierRiskLevel


class BedrockSupplierAnalysisPayload(BaseModel):
    risk_level: SupplierRiskLevel
    recommended_action: SupplierRecommendedAction
    missing_documents: list[str] = Field(default_factory=list)
    policy_violations: list[str] = Field(default_factory=list)
    summary: str = Field(min_length=1, max_length=1000)
    confidence: float = Field(ge=0.0, le=1.0)
