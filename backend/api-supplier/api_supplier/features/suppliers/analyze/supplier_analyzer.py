from dataclasses import dataclass, field
from typing import Protocol

from api_supplier.domain.entities.supplier import Supplier
from api_supplier.domain.enums.supplier_recommended_action import (
    SupplierRecommendedAction,
)
from api_supplier.domain.enums.supplier_risk_level import SupplierRiskLevel
from api_supplier.features.suppliers.analyze.policy_context import PolicyContext


@dataclass(frozen=True, slots=True)
class SupplierAnalysisResult:
    risk_level: SupplierRiskLevel
    recommended_action: SupplierRecommendedAction
    summary: str
    confidence: float
    missing_documents: tuple[str, ...] = field(default_factory=tuple)
    policy_violations: tuple[str, ...] = field(default_factory=tuple)
    retrieved_policy_ids: tuple[str, ...] = field(default_factory=tuple)


class SupplierAnalyzer(Protocol):
    async def analyze(
        self,
        supplier: Supplier,
        policies: tuple[PolicyContext, ...],
    ) -> SupplierAnalysisResult:
        ...
