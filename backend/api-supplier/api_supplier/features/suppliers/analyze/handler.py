import logging
from time import perf_counter

from api_supplier.domain.entities.supplier import Supplier
from api_supplier.domain.enums.supplier_recommended_action import (
    SupplierRecommendedAction,
)
from api_supplier.domain.enums.supplier_risk_level import (
    SupplierRiskLevel,
)
from api_supplier.features.suppliers.analyze.command import (
    AnalyzeSupplierCommand,
)
from api_supplier.features.suppliers.analyze.exceptions import (
    SupplierNotFoundError,
)
from api_supplier.features.suppliers.analyze.policy_retriever import (
    PolicyRetriever,
)
from api_supplier.features.suppliers.analyze.supplier_analyzer import (
    SupplierAnalyzer,
    SupplierAnalysisResult,
)
from api_supplier.shared.observability import (
    get_tracer,
    record_exception,
)
from api_supplier.shared.unit_of_work import (
    SupplierUnitOfWork,
)


logger = logging.getLogger(__name__)
tracer = get_tracer("api-supplier")


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
        started = perf_counter()
        supplier_id = str(command.supplier_id)

        with tracer.start_as_current_span(
            "feature.AnalyzeSupplier"
        ) as feature_span:
            feature_span.set_attribute(
                "app.feature",
                "AnalyzeSupplier",
            )
            feature_span.set_attribute(
                "app.supplier_id",
                supplier_id,
            )

            logger.info(
                "supplier analysis started",
                extra={
                    "feature": "AnalyzeSupplier",
                    "supplier_id": supplier_id,
                },
            )

            try:
                with tracer.start_as_current_span(
                    "repository.supplier.get_by_id"
                ) as repository_span:
                    repository_span.set_attribute(
                        "app.supplier_id",
                        supplier_id,
                    )

                    async with self._unit_of_work as uow:
                        supplier = (
                            await uow.suppliers.get_by_id(
                                command.supplier_id
                            )
                        )

                if supplier is None:
                    raise SupplierNotFoundError(
                        command.supplier_id
                    )

                retrieval_query = (
                    self._build_retrieval_query(
                        supplier
                    )
                )

                retrieval_started = perf_counter()
                logger.info(
                    "policy retrieval started",
                    extra={
                        "feature": "AnalyzeSupplier",
                        "component": "PolicyRetriever",
                        "supplier_id": supplier_id,
                    },
                )

                with tracer.start_as_current_span(
                    "rag.policy_retrieval"
                ) as retrieval_span:
                    retrieval_span.set_attribute(
                        "app.supplier_id",
                        supplier_id,
                    )
                    policies = (
                        await self._policy_retriever.retrieve(
                            retrieval_query,
                            limit=5,
                        )
                    )
                    retrieval_span.set_attribute(
                        "rag.document_count",
                        len(policies),
                    )

                logger.info(
                    "policy retrieval completed",
                    extra={
                        "feature": "AnalyzeSupplier",
                        "component": "PolicyRetriever",
                        "supplier_id": supplier_id,
                        "document_count": len(policies),
                        "duration_ms": round(
                            (
                                perf_counter()
                                - retrieval_started
                            )
                            * 1000,
                            2,
                        ),
                    },
                )

                if not policies:
                    result = SupplierAnalysisResult(
                        risk_level=(
                            SupplierRiskLevel.MEDIUM
                        ),
                        recommended_action=(
                            SupplierRecommendedAction
                            .HUMAN_REVIEW
                        ),
                        summary=(
                            "No relevant policy was "
                            "retrieved for this supplier."
                        ),
                        confidence=0.0,
                        missing_documents=(),
                        policy_violations=(),
                        retrieved_policy_ids=(),
                    )

                    logger.info(
                        "supplier analysis completed without policy evidence",
                        extra={
                            "feature": "AnalyzeSupplier",
                            "supplier_id": supplier_id,
                            "document_count": 0,
                            "risk_level": (
                                result.risk_level.value
                            ),
                            "recommended_action": (
                                result
                                .recommended_action
                                .value
                            ),
                            "confidence": (
                                result.confidence
                            ),
                            "duration_ms": round(
                                (
                                    perf_counter()
                                    - started
                                )
                                * 1000,
                                2,
                            ),
                        },
                    )
                    return result

                ai_started = perf_counter()
                logger.info(
                    "AI supplier analysis started",
                    extra={
                        "feature": "AnalyzeSupplier",
                        "component": "SupplierAnalyzer",
                        "supplier_id": supplier_id,
                        "document_count": len(policies),
                    },
                )

                with tracer.start_as_current_span(
                    "ai.supplier_analysis"
                ) as ai_span:
                    ai_span.set_attribute(
                        "app.supplier_id",
                        supplier_id,
                    )
                    ai_span.set_attribute(
                        "rag.document_count",
                        len(policies),
                    )

                    analysis = (
                        await self._supplier_analyzer
                        .analyze(
                            supplier,
                            policies,
                        )
                    )

                    ai_span.set_attribute(
                        "ai.risk_level",
                        analysis.risk_level.value,
                    )
                    ai_span.set_attribute(
                        "ai.recommended_action",
                        analysis
                        .recommended_action.value,
                    )
                    ai_span.set_attribute(
                        "ai.confidence",
                        analysis.confidence,
                    )

                logger.info(
                    "AI supplier analysis completed",
                    extra={
                        "feature": "AnalyzeSupplier",
                        "component": "SupplierAnalyzer",
                        "supplier_id": supplier_id,
                        "risk_level": (
                            analysis.risk_level.value
                        ),
                        "recommended_action": (
                            analysis
                            .recommended_action.value
                        ),
                        "confidence": (
                            analysis.confidence
                        ),
                        "duration_ms": round(
                            (
                                perf_counter()
                                - ai_started
                            )
                            * 1000,
                            2,
                        ),
                    },
                )

                analysis = SupplierAnalysisResult(
                    risk_level=analysis.risk_level,
                    recommended_action=(
                        analysis.recommended_action
                    ),
                    summary=analysis.summary,
                    confidence=analysis.confidence,
                    missing_documents=(
                        analysis.missing_documents
                    ),
                    policy_violations=(
                        analysis.policy_violations
                    ),
                    retrieved_policy_ids=tuple(
                        dict.fromkeys(
                            policy.document_id
                            for policy in policies
                        )
                    ),
                )

                result = (
                    self._apply_deterministic_rules(
                        analysis
                    )
                )

                feature_span.set_attribute(
                    "ai.risk_level",
                    result.risk_level.value,
                )
                feature_span.set_attribute(
                    "ai.recommended_action",
                    result.recommended_action.value,
                )
                feature_span.set_attribute(
                    "ai.confidence",
                    result.confidence,
                )

                logger.info(
                    "supplier analysis completed",
                    extra={
                        "feature": "AnalyzeSupplier",
                        "supplier_id": supplier_id,
                        "risk_level": (
                            result.risk_level.value
                        ),
                        "recommended_action": (
                            result
                            .recommended_action.value
                        ),
                        "confidence": result.confidence,
                        "document_count": len(policies),
                        "duration_ms": round(
                            (
                                perf_counter()
                                - started
                            )
                            * 1000,
                            2,
                        ),
                    },
                )

                return result

            except Exception as exc:
                record_exception(
                    feature_span,
                    exc,
                )
                logger.exception(
                    "supplier analysis failed",
                    extra={
                        "feature": "AnalyzeSupplier",
                        "supplier_id": supplier_id,
                        "duration_ms": round(
                            (
                                perf_counter()
                                - started
                            )
                            * 1000,
                            2,
                        ),
                    },
                )
                raise

    @staticmethod
    def _build_retrieval_query(
        supplier: Supplier,
    ) -> str:
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
            or bool(
                analysis.missing_documents
            )
            or analysis.risk_level
            == SupplierRiskLevel.HIGH
        )

        if not requires_human_review:
            return analysis

        return SupplierAnalysisResult(
            risk_level=analysis.risk_level,
            recommended_action=(
                SupplierRecommendedAction
                .HUMAN_REVIEW
            ),
            summary=analysis.summary,
            confidence=analysis.confidence,
            missing_documents=(
                analysis.missing_documents
            ),
            policy_violations=(
                analysis.policy_violations
            ),
            retrieved_policy_ids=(
                analysis.retrieved_policy_ids
            ),
        )
