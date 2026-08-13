from backend.app.domain.entities.supplier import Supplier
from backend.app.domain.enums.supplier_recommended_action import (
    SupplierRecommendedAction,
)
from backend.app.domain.enums.supplier_risk_level import SupplierRiskLevel
from backend.app.features.suppliers.analyze.command import AnalyzeSupplierCommand
from backend.app.features.suppliers.analyze.exceptions import SupplierNotFoundError
from backend.app.features.suppliers.analyze.policy_retriever import PolicyRetriever
from backend.app.features.suppliers.analyze.supplier_analyzer import (
    SupplierAnalyzer,
    SupplierAnalysisResult,
)
from backend.app.shared.unit_of_work import SupplierUnitOfWork


class AnalyzeSupplierHandler:
    def __init__(
        self,
        unit_of_work: SupplierUnitOfWork,
        supplier_analyzer: SupplierAnalyzer,
        policy_retriever: PolicyRetriever,
    ) -> None:
        self._unit_of_work = unit_of_work
        self._supplier_analyzer = supplier_analyzer
        self._policy_retriever = policy_retriever

    async def handle(
        self,
        command: AnalyzeSupplierCommand,
    ) -> SupplierAnalysisResult:
        async with self._unit_of_work as uow:
            supplier = await uow.suppliers.get_by_id(command.supplier_id)

        if supplier is None:
            raise SupplierNotFoundError(command.supplier_id)

        retrieval_query = self._build_retrieval_query(supplier)
        policies = await self._policy_retriever.retrieve(
            retrieval_query,
            limit=5,
        )

        if not policies:
            return SupplierAnalysisResult(
                risk_level=SupplierRiskLevel.MEDIUM,
                recommended_action=SupplierRecommendedAction.HUMAN_REVIEW,
                summary="No relevant policy was retrieved for this supplier.",
                confidence=0.0,
                missing_documents=(),
                policy_violations=(),
                retrieved_policy_ids=(),
            )

        analysis = await self._supplier_analyzer.analyze(
            supplier,
            policies,
        )

        analysis = SupplierAnalysisResult(
            risk_level=analysis.risk_level,
            recommended_action=analysis.recommended_action,
            summary=analysis.summary,
            confidence=analysis.confidence,
            missing_documents=analysis.missing_documents,
            policy_violations=analysis.policy_violations,
            retrieved_policy_ids=tuple(
                dict.fromkeys(policy.document_id for policy in policies)
            ),
        )

        return self._apply_deterministic_rules(analysis)

    @staticmethod
    def _build_retrieval_query(supplier: Supplier) -> str:
        return (
            "Supplier onboarding, required documents, compliance, "
            "risk review and approval rules for "
            f"country {supplier.address.country}. "
            f"Supplier tax identifier: {supplier.tax_id}."
        )

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
            retrieved_policy_ids=analysis.retrieved_policy_ids,
        )
