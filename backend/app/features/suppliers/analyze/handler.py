from backend.app.features.suppliers.analyze.supplier_analyzer import (
    SupplierAnalyzer,
    SupplierAnalysisResult,
)
from backend.app.domain.enums.supplier_recommended_action import (
    SupplierRecommendedAction,
)
from backend.app.domain.enums.supplier_risk_level import SupplierRiskLevel
from backend.app.domain.repositories.supplier_repository import SupplierRepository
from backend.app.features.suppliers.analyze.command import AnalyzeSupplierCommand
from backend.app.features.suppliers.analyze.exceptions import SupplierNotFoundError


class AnalyzeSupplierHandler:
    def __init__(
        self,
        supplier_repository: SupplierRepository,
        supplier_analyzer: SupplierAnalyzer,
    ) -> None:
        self._supplier_repository = supplier_repository
        self._supplier_analyzer = supplier_analyzer

    async def handle(
        self,
        command: AnalyzeSupplierCommand,
    ) -> SupplierAnalysisResult:
        supplier = await self._supplier_repository.get_by_id(command.supplier_id)

        if supplier is None:
            raise SupplierNotFoundError(command.supplier_id)

        analysis = await self._supplier_analyzer.analyze(supplier)
        return self._apply_deterministic_rules(analysis)

    @staticmethod
    def _apply_deterministic_rules(
        analysis: SupplierAnalysisResult,
    ) -> SupplierAnalysisResult:
        requires_human_review = (
            analysis.confidence < 0.80
            or bool(analysis.missing_documents)
            or analysis.risk_level == SupplierRiskLevel.HIGH
        )

        if not requires_human_review:
            return analysis

        return SupplierAnalysisResult(
            risk_level=analysis.risk_level,
            recommended_action=SupplierRecommendedAction.HUMAN_REVIEW,
            summary=analysis.summary,
            confidence=analysis.confidence,
            missing_documents=analysis.missing_documents,
            policy_violations=analysis.policy_violations,
        )
