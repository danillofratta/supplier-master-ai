from pydantic import BaseModel, Field

from backend.app.domain.enums.supplier_recommended_action import (
    SupplierRecommendedAction,
)
from backend.app.domain.enums.supplier_risk_level import SupplierRiskLevel
from backend.app.features.suppliers.analyze.supplier_analyzer import (
    SupplierAnalysisResult,
)


class AnalyzeSupplierResponse(BaseModel):
    risk_level: SupplierRiskLevel
    recommended_action: SupplierRecommendedAction
    missing_documents: list[str] = Field(default_factory=list)
    policy_violations: list[str] = Field(default_factory=list)
    retrieved_policy_ids: list[str] = Field(default_factory=list)
    summary: str
    confidence: float

    @classmethod
    def from_result(
        cls,
        result: SupplierAnalysisResult,
    ) -> "AnalyzeSupplierResponse":
        return cls(
            risk_level=result.risk_level,
            recommended_action=result.recommended_action,
            missing_documents=list(result.missing_documents),
            policy_violations=list(result.policy_violations),
            retrieved_policy_ids=list(result.retrieved_policy_ids),
            summary=result.summary,
            confidence=result.confidence,
        )
