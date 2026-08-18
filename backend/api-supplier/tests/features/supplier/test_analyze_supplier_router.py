from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient

from api_supplier.features.suppliers.analyze.supplier_analyzer import SupplierAnalysisResult
from api_supplier.bootstrap.dependencies import get_analyze_supplier_handler
from api_supplier.domain.enums.supplier_recommended_action import (
    SupplierRecommendedAction,
)
from api_supplier.domain.enums.supplier_risk_level import SupplierRiskLevel
from api_supplier.features.suppliers.analyze.endpoint import router
from api_supplier.features.suppliers.exception_handlers import (
    register_exception_handlers,
)


class FakeAnalyzeSupplierHandler:
    async def handle(self, command) -> SupplierAnalysisResult:
        return SupplierAnalysisResult(
            risk_level=SupplierRiskLevel.MEDIUM,
            recommended_action=SupplierRecommendedAction.HUMAN_REVIEW,
            missing_documents=("bank_account_confirmation",),
            policy_violations=(),
            summary="Manual review is required.",
            confidence=0.91
        )


def test_analyze_supplier_returns_api_response() -> None:
    app = FastAPI()
    register_exception_handlers(app)
    app.include_router(router)
    app.dependency_overrides[get_analyze_supplier_handler] = (
        lambda: FakeAnalyzeSupplierHandler()
    )
    supplier_id = uuid4()

    with TestClient(app) as client:
        response = client.post(f"/v1/suppliers/{supplier_id}/analysis")

    assert response.status_code == 200
    assert response.json() == {
        "risk_level": "medium",
        "recommended_action": "human_review",
        "missing_documents": ["bank_account_confirmation"],
        "policy_violations": [],
        "retrieved_policy_ids": [],
        "summary": "Manual review is required.",
        "confidence": 0.91,
    }
