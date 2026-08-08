from uuid import uuid4

import pytest

from backend.app.features.suppliers.analyze.supplier_analyzer import (
    SupplierAnalysisResult,
)
from backend.app.domain.enums.supplier_recommended_action import (
    SupplierRecommendedAction,
)
from backend.app.domain.enums.supplier_risk_level import SupplierRiskLevel
from backend.app.features.suppliers.analyze.command import AnalyzeSupplierCommand
from backend.app.features.suppliers.analyze.exceptions import SupplierNotFoundError
from backend.app.features.suppliers.analyze.handler import AnalyzeSupplierHandler
from backend.app.infrastructure.repositories.supplier_repository import (
    InMemorySupplierRepository,
)
from backend.tests.features.supplier.create_supplier_router_test import (
    build_supplier,
)


class FakeSupplierAnalyzer:
    def __init__(self, analysis: SupplierAnalysisResult) -> None:
        self.analysis = analysis
        self.received_supplier = None

    async def analyze(self, supplier):
        self.received_supplier = supplier
        return self.analysis


@pytest.mark.asyncio
async def test_high_risk_supplier_requires_human_review() -> None:
    supplier = build_supplier(uuid4())
    repository = InMemorySupplierRepository()
    await repository.add(supplier)

    analyzer = FakeSupplierAnalyzer(
        SupplierAnalysisResult(
            risk_level=SupplierRiskLevel.HIGH,
            recommended_action=SupplierRecommendedAction.APPROVE,
            missing_documents=(),
            policy_violations=(),
            summary="Potential supplier risk.",
            confidence=0.95,
        )
    )
    handler = AnalyzeSupplierHandler(repository, analyzer)

    result = await handler.handle(
        AnalyzeSupplierCommand(supplier_id=supplier.supplier_id)
    )

    assert result.recommended_action == SupplierRecommendedAction.HUMAN_REVIEW
    assert analyzer.received_supplier is supplier


@pytest.mark.asyncio
async def test_missing_documents_require_human_review() -> None:
    supplier = build_supplier(uuid4())
    repository = InMemorySupplierRepository()
    await repository.add(supplier)

    analyzer = FakeSupplierAnalyzer(
        SupplierAnalysisResult(
            risk_level=SupplierRiskLevel.LOW,
            recommended_action=SupplierRecommendedAction.APPROVE,
            missing_documents=("bank_account_confirmation",),
            policy_violations=(),
            summary="A mandatory document is missing.",
            confidence=0.95,
        )
    )
    handler = AnalyzeSupplierHandler(repository, analyzer)

    result = await handler.handle(
        AnalyzeSupplierCommand(supplier_id=supplier.supplier_id)
    )

    assert result.recommended_action == SupplierRecommendedAction.HUMAN_REVIEW


@pytest.mark.asyncio
async def test_supplier_not_found() -> None:
    repository = InMemorySupplierRepository()
    analyzer = FakeSupplierAnalyzer(
        SupplierAnalysisResult(
            risk_level=SupplierRiskLevel.LOW,
            recommended_action=SupplierRecommendedAction.APPROVE,
            summary="Supplier looks valid.",
            confidence=0.95,
        )
    )
    handler = AnalyzeSupplierHandler(repository, analyzer)
    supplier_id = uuid4()

    with pytest.raises(SupplierNotFoundError):
        await handler.handle(AnalyzeSupplierCommand(supplier_id=supplier_id))
