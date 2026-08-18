from uuid import uuid4

import pytest

from api_supplier.domain.enums.supplier_recommended_action import (
    SupplierRecommendedAction,
)
from api_supplier.domain.enums.supplier_risk_level import SupplierRiskLevel
from api_supplier.features.suppliers.analyze.command import AnalyzeSupplierCommand
from api_supplier.features.suppliers.analyze.exceptions import SupplierNotFoundError
from api_supplier.features.suppliers.analyze.handler import AnalyzeSupplierHandler
from api_supplier.features.suppliers.analyze.policy_context import PolicyContext
from api_supplier.features.suppliers.analyze.supplier_analyzer import (
    SupplierAnalysisResult,
)
from api_supplier.infrastructure.persistence.in_memory_unit_of_work import (
    InMemorySupplierUnitOfWork,
)
from tests.features.supplier.create_supplier_router_test import (
    build_supplier,
)


class FakeSupplierAnalyzer:
    def __init__(self, analysis: SupplierAnalysisResult) -> None:
        self.analysis = analysis
        self.received_supplier = None
        self.received_policies = None

    async def analyze(self, supplier, policies):
        self.received_supplier = supplier
        self.received_policies = policies
        return self.analysis


class FakePolicyRetriever:
    def __init__(self, policies: tuple[PolicyContext, ...]) -> None:
        self._policies = policies
        self.received_query: str | None = None
        self.received_limit: int | None = None

    async def retrieve(
        self,
        query: str,
        *,
        limit: int = 5,
    ) -> tuple[PolicyContext, ...]:
        self.received_query = query
        self.received_limit = limit
        return self._policies


def build_analysis_result(
    *,
    risk_level: SupplierRiskLevel = SupplierRiskLevel.LOW,
    recommended_action: SupplierRecommendedAction = SupplierRecommendedAction.APPROVE,
    missing_documents: tuple[str, ...] = (),
    confidence: float = 0.95,
) -> SupplierAnalysisResult:
    return SupplierAnalysisResult(
        risk_level=risk_level,
        recommended_action=recommended_action,
        missing_documents=missing_documents,
        policy_violations=(),
        summary="Supplier analysis.",
        confidence=confidence,
    )


def build_policy() -> PolicyContext:
    return PolicyContext(
        document_id="policy-001",
        chunk_id="chunk-001",
        title="Bank Verification Policy",
        content="Bank ownership confirmation is mandatory.",
        policy_type="compliance",
        version="1.0",
        effective_date="2026-01-01",
        score=0.94,
    )


@pytest.mark.asyncio
async def test_analyze_supplier_uses_retrieved_policies() -> None:
    supplier = build_supplier(uuid4())
    uow = InMemorySupplierUnitOfWork()
    await uow.suppliers.add(supplier)

    policies = (build_policy(),)
    retriever = FakePolicyRetriever(policies)
    analyzer = FakeSupplierAnalyzer(build_analysis_result())

    handler = AnalyzeSupplierHandler(
        unit_of_work=uow,
        policy_retriever=retriever,
        supplier_analyzer=analyzer,
    )

    result = await handler.handle(
        AnalyzeSupplierCommand(supplier_id=supplier.supplier_id)
    )

    assert retriever.received_query is not None
    assert retriever.received_limit == 5
    assert analyzer.received_policies == policies
    assert result.retrieved_policy_ids == ("policy-001",)


@pytest.mark.asyncio
async def test_high_risk_supplier_requires_human_review() -> None:
    supplier = build_supplier(uuid4())
    uow = InMemorySupplierUnitOfWork()
    await uow.suppliers.add(supplier)

    analyzer = FakeSupplierAnalyzer(
        build_analysis_result(
            risk_level=SupplierRiskLevel.HIGH,
            recommended_action=SupplierRecommendedAction.APPROVE,
        )
    )
    handler = AnalyzeSupplierHandler(
        uow,
        analyzer,
        FakePolicyRetriever((build_policy(),)),
    )

    result = await handler.handle(
        AnalyzeSupplierCommand(supplier_id=supplier.supplier_id)
    )

    assert result.recommended_action == SupplierRecommendedAction.HUMAN_REVIEW


@pytest.mark.asyncio
async def test_missing_documents_require_human_review() -> None:
    supplier = build_supplier(uuid4())
    uow = InMemorySupplierUnitOfWork()
    await uow.suppliers.add(supplier)

    analyzer = FakeSupplierAnalyzer(
        build_analysis_result(
            missing_documents=("bank_account_confirmation",),
        )
    )
    handler = AnalyzeSupplierHandler(
        uow,
        analyzer,
        FakePolicyRetriever((build_policy(),)),
    )

    result = await handler.handle(
        AnalyzeSupplierCommand(supplier_id=supplier.supplier_id)
    )

    assert result.recommended_action == SupplierRecommendedAction.HUMAN_REVIEW


@pytest.mark.asyncio
async def test_no_policy_requires_human_review_without_calling_ai() -> None:
    supplier = build_supplier(uuid4())
    uow = InMemorySupplierUnitOfWork()
    await uow.suppliers.add(supplier)

    analyzer = FakeSupplierAnalyzer(build_analysis_result())
    handler = AnalyzeSupplierHandler(
        uow,
        analyzer,
        FakePolicyRetriever(()),
    )

    result = await handler.handle(
        AnalyzeSupplierCommand(supplier_id=supplier.supplier_id)
    )

    assert result.recommended_action == SupplierRecommendedAction.HUMAN_REVIEW
    assert result.confidence == 0.0
    assert analyzer.received_supplier is None


@pytest.mark.asyncio
async def test_supplier_not_found() -> None:
    uow = InMemorySupplierUnitOfWork()
    analyzer = FakeSupplierAnalyzer(build_analysis_result())
    handler = AnalyzeSupplierHandler(
        uow,
        analyzer,
        FakePolicyRetriever((build_policy(),)),
    )

    with pytest.raises(SupplierNotFoundError):
        await handler.handle(
            AnalyzeSupplierCommand(supplier_id=uuid4())
        )
