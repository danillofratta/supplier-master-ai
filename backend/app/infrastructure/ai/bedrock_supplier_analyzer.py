import asyncio
import json
import logging
from typing import Any

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from pydantic import ValidationError

from backend.app.features.suppliers.analyze.supplier_analyzer import (
    SupplierAnalyzer,
    SupplierAnalysisResult,
)
from backend.app.domain.entities.supplier import Supplier
from backend.app.features.suppliers.analyze.prompt import (
    SYSTEM_PROMPT,
    build_supplier_analysis_prompt,
)
from backend.app.application.ai.exceptions import (
    InvalidSupplierAnalysisResponseError,
    SupplierAnalysisProviderError,
)
from backend.app.infrastructure.ai.models import BedrockSupplierAnalysisPayload

logger = logging.getLogger(__name__)


class BedrockSupplierAnalyzer(SupplierAnalyzer):
    def __init__(
        self,
        *,
        region_name: str,
        model_id: str,
        temperature: float,
        max_tokens: int,
    ) -> None:
        self._model_id = model_id
        self._temperature = temperature
        self._max_tokens = max_tokens
        self._client = boto3.client(
            "bedrock-runtime",
            region_name=region_name,
        )

    async def analyze(self, supplier: Supplier) -> SupplierAnalysisResult:
        user_prompt = build_supplier_analysis_prompt(supplier)

        try:
            response = await asyncio.to_thread(self._converse, user_prompt)
        except (ClientError, BotoCoreError) as exc:
            logger.exception(
                "Amazon Bedrock failed while analyzing supplier %s.",
                supplier.supplier_id,
            )
            raise SupplierAnalysisProviderError(
                "Unable to analyze the supplier using Amazon Bedrock."
            ) from exc

        response_text = self._extract_text(response)

        try:
            payload = BedrockSupplierAnalysisPayload.model_validate_json(
                response_text
            )
        except (ValidationError, json.JSONDecodeError) as exc:
            logger.exception(
                "Amazon Bedrock returned an invalid supplier analysis."
            )
            raise InvalidSupplierAnalysisResponseError(
                "Amazon Bedrock returned an invalid analysis response."
            ) from exc

        return SupplierAnalysisResult(
            risk_level=payload.risk_level,
            recommended_action=payload.recommended_action,
            summary=payload.summary,
            confidence=payload.confidence,
            missing_documents=tuple(payload.missing_documents),
            policy_violations=tuple(payload.policy_violations),
        )

    def _converse(self, user_prompt: str) -> dict[str, Any]:
        return self._client.converse(
            modelId=self._model_id,
            system=[{"text": SYSTEM_PROMPT}],
            messages=[
                {
                    "role": "user",
                    "content": [{"text": user_prompt}],
                }
            ],
            inferenceConfig={
                "temperature": self._temperature,
                "maxTokens": self._max_tokens,
            },
        )

    @staticmethod
    def _extract_text(response: dict[str, Any]) -> str:
        try:
            content_blocks = response["output"]["message"]["content"]
            text_blocks = [
                block["text"]
                for block in content_blocks
                if isinstance(block, dict) and "text" in block
            ]
            if not text_blocks:
                raise KeyError("No text block was returned.")
            return "".join(text_blocks).strip()
        except (KeyError, TypeError) as exc:
            raise InvalidSupplierAnalysisResponseError(
                "Amazon Bedrock response did not contain text."
            ) from exc
