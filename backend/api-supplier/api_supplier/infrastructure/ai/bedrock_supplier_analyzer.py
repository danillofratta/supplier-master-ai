import asyncio
import json
import logging
from time import perf_counter
from typing import Any

import boto3
from botocore.exceptions import (
    BotoCoreError,
    ClientError,
)
from pydantic import ValidationError

from api_supplier.domain.entities.supplier import (
    Supplier,
)
from api_supplier.features.suppliers.analyze.exceptions import (
    InvalidSupplierAnalysisResponseError,
    SupplierAnalysisProviderError,
)
from api_supplier.features.suppliers.analyze.prompt import (
    SYSTEM_PROMPT,
    build_supplier_analysis_prompt,
)
from api_supplier.features.suppliers.analyze.supplier_analyzer import (
    SupplierAnalyzer,
    SupplierAnalysisResult,
)
from api_supplier.infrastructure.ai.models import (
    BedrockSupplierAnalysisPayload,
)
from api_supplier.shared.observability import (
    get_tracer,
    record_exception,
)


logger = logging.getLogger(__name__)
tracer = get_tracer("api-supplier")


class BedrockSupplierAnalyzer(
    SupplierAnalyzer
):
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

    async def analyze(
        self,
        supplier: Supplier,
        policies,
    ) -> SupplierAnalysisResult:
        started = perf_counter()

        with tracer.start_as_current_span(
            "bedrock.supplier_analysis"
        ) as span:
            span.set_attribute(
                "gen_ai.system",
                "aws.bedrock",
            )
            span.set_attribute(
                "gen_ai.request.model",
                self._model_id,
            )
            span.set_attribute(
                "app.supplier_id",
                str(supplier.supplier_id),
            )
            span.set_attribute(
                "rag.document_count",
                len(policies),
            )

            user_prompt = (
                build_supplier_analysis_prompt(
                    supplier,
                    policies,
                )
            )

            logger.info(
                "Bedrock supplier analysis request started",
                extra={
                    "component": (
                        "BedrockSupplierAnalyzer"
                    ),
                    "supplier_id": str(
                        supplier.supplier_id
                    ),
                    "model_id": self._model_id,
                    "document_count": len(
                        policies
                    ),
                },
            )

            try:
                response = await asyncio.to_thread(
                    self._converse,
                    user_prompt,
                )
            except (
                ClientError,
                BotoCoreError,
            ) as exc:
                record_exception(span, exc)
                logger.exception(
                    "Amazon Bedrock supplier analysis request failed",
                    extra={
                        "component": (
                            "BedrockSupplierAnalyzer"
                        ),
                        "supplier_id": str(
                            supplier.supplier_id
                        ),
                        "model_id": (
                            self._model_id
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
                raise SupplierAnalysisProviderError(
                    "Unable to analyze the supplier using Amazon Bedrock."
                ) from exc

            response_text = self._extract_text(
                response
            )

            try:
                payload = (
                    BedrockSupplierAnalysisPayload
                    .model_validate_json(
                        response_text
                    )
                )
            except (
                ValidationError,
                json.JSONDecodeError,
            ) as exc:
                record_exception(span, exc)
                logger.exception(
                    "Amazon Bedrock returned an invalid supplier analysis",
                    extra={
                        "component": (
                            "BedrockSupplierAnalyzer"
                        ),
                        "supplier_id": str(
                            supplier.supplier_id
                        ),
                        "model_id": (
                            self._model_id
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
                raise (
                    InvalidSupplierAnalysisResponseError(
                        "Amazon Bedrock returned an invalid analysis response."
                    )
                ) from exc

            result = SupplierAnalysisResult(
                risk_level=payload.risk_level,
                recommended_action=(
                    payload.recommended_action
                ),
                summary=payload.summary,
                confidence=payload.confidence,
                missing_documents=tuple(
                    payload.missing_documents
                ),
                policy_violations=tuple(
                    payload.policy_violations
                ),
                retrieved_policy_ids=tuple(
                    dict.fromkeys(
                        policy.document_id
                        for policy in policies
                    )
                ),
            )

            span.set_attribute(
                "ai.risk_level",
                result.risk_level.value,
            )
            span.set_attribute(
                "ai.recommended_action",
                result.recommended_action.value,
            )
            span.set_attribute(
                "ai.confidence",
                result.confidence,
            )

            logger.info(
                "Bedrock supplier analysis request completed",
                extra={
                    "component": (
                        "BedrockSupplierAnalyzer"
                    ),
                    "supplier_id": str(
                        supplier.supplier_id
                    ),
                    "model_id": self._model_id,
                    "risk_level": (
                        result.risk_level.value
                    ),
                    "recommended_action": (
                        result
                        .recommended_action.value
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

    def _converse(
        self,
        user_prompt: str,
    ) -> dict[str, Any]:
        return self._client.converse(
            modelId=self._model_id,
            system=[
                {
                    "text": SYSTEM_PROMPT
                }
            ],
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "text": (
                                user_prompt
                            )
                        }
                    ],
                }
            ],
            inferenceConfig={
                "temperature": (
                    self._temperature
                ),
                "maxTokens": (
                    self._max_tokens
                ),
            },
        )

    @staticmethod
    def _extract_text(
        response: dict[str, Any],
    ) -> str:
        try:
            content_blocks = response[
                "output"
            ]["message"]["content"]

            text_blocks = [
                block["text"]
                for block in content_blocks
                if isinstance(
                    block,
                    dict,
                )
                and "text" in block
            ]

            if not text_blocks:
                raise KeyError(
                    "No text block was returned."
                )

            return "".join(
                text_blocks
            ).strip()

        except (
            KeyError,
            TypeError,
        ) as exc:
            raise (
                InvalidSupplierAnalysisResponseError(
                    "Amazon Bedrock response did not contain text."
                )
            ) from exc
