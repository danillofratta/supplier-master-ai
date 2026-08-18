import json
from uuid import uuid4

import pytest

from api_supplier.domain.enums.supplier_recommended_action import (
    SupplierRecommendedAction,
)
from api_supplier.domain.enums.supplier_risk_level import SupplierRiskLevel
from api_supplier.infrastructure.ai.bedrock_supplier_analyzer import (
    BedrockSupplierAnalyzer,
)
from api_supplier.features.suppliers.analyze.exceptions import (
    InvalidSupplierAnalysisResponseError,
)
from api_supplier.features.suppliers.analyze.policy_context import PolicyContext
from tests.features.supplier.create_supplier_router_test import (
    build_supplier,
)


class FakeBedrockRuntimeClient:
    def __init__(self, response_text: str) -> None:
        self.response_text = response_text

    def converse(self, **kwargs):
        return {
            "output": {
                "message": {
                    "content": [{"text": self.response_text}],
                }
            }
        }


def build_analyzer(response_text: str) -> BedrockSupplierAnalyzer:
    analyzer = object.__new__(BedrockSupplierAnalyzer)
    analyzer._model_id = "test-model"
    analyzer._temperature = 0.0
    analyzer._max_tokens = 1000
    analyzer._client = FakeBedrockRuntimeClient(response_text)
    return analyzer


@pytest.mark.asyncio
async def test_bedrock_response_is_mapped_to_application_result() -> None:
    response_text = json.dumps(
        {
            "risk_level": "low",
            "recommended_action": "approve",
            "missing_documents": [],
            "policy_violations": [],
            "summary": "Supplier information is complete.",
            "confidence": 0.94,
        }
    )
    analyzer = build_analyzer(response_text)

    result = await analyzer.analyze(
        build_supplier(uuid4()),
        (
            PolicyContext(
                document_id="policy-001",
                chunk_id="chunk-001",
                title="Policy",
                content="Supplier policy context.",
                policy_type="compliance",
                version="1.0",
                effective_date="2026-01-01",
                score=0.9,
            ),
        ),
    )

    assert result.risk_level == SupplierRiskLevel.LOW
    assert result.recommended_action == SupplierRecommendedAction.APPROVE
    assert result.confidence == 0.94


@pytest.mark.asyncio
async def test_invalid_bedrock_response_is_rejected() -> None:
    analyzer = build_analyzer('{"risk_level": "unknown"}')

    with pytest.raises(InvalidSupplierAnalysisResponseError):
        await analyzer.analyze(
            build_supplier(uuid4()),
            (
                PolicyContext(
                    document_id="policy-001",
                    chunk_id="chunk-001",
                    title="Policy",
                    content="Supplier policy context.",
                    policy_type="compliance",
                    version="1.0",
                    effective_date="2026-01-01",
                    score=0.9,
                ),
            ),
        )
