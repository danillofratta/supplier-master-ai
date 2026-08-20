import asyncio
import json
import logging
from time import perf_counter
from typing import Any

from api_supplier.features.policies.ingest.embedding_provider import (
    EmbeddingProvider,
)
from api_supplier.shared.observability import (
    get_tracer,
    record_exception,
)


logger = logging.getLogger(__name__)
tracer = get_tracer("api-supplier")


class InvalidEmbeddingResponseError(
    Exception
):
    pass


class TitanEmbeddingProvider(
    EmbeddingProvider
):
    def __init__(
        self,
        *,
        region_name: str,
        model_id: str = (
            "amazon.titan-embed-text-v2:0"
        ),
        dimensions: int = 1024,
        normalize: bool = True,
    ) -> None:
        if dimensions not in {
            256,
            512,
            1024,
        }:
            raise ValueError(
                "Titan embedding dimensions must be 256, 512, or 1024."
            )

        import boto3

        self._client = boto3.client(
            "bedrock-runtime",
            region_name=region_name,
        )
        self._model_id = model_id
        self._dimensions = dimensions
        self._normalize = normalize

    @property
    def dimensions(self) -> int:
        return self._dimensions

    async def generate(
        self,
        text: str,
    ) -> tuple[float, ...]:
        if not text.strip():
            raise ValueError(
                "Embedding text cannot be empty."
            )

        started = perf_counter()

        with tracer.start_as_current_span(
            "bedrock.embedding.generate"
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
                "embedding.dimensions",
                self._dimensions,
            )

            logger.info(
                "Bedrock embedding request started",
                extra={
                    "component": (
                        "TitanEmbeddingProvider"
                    ),
                    "model_id": self._model_id,
                    "embedding_dimensions": (
                        self._dimensions
                    ),
                },
            )

            try:
                response = await asyncio.to_thread(
                    self._invoke_model,
                    text,
                )

                payload = json.loads(
                    response["body"].read()
                )
                embedding = payload.get(
                    "embedding"
                )

                if not isinstance(
                    embedding,
                    list,
                ):
                    raise (
                        InvalidEmbeddingResponseError(
                            "Titan did not return a valid embedding."
                        )
                    )

                if (
                    len(embedding)
                    != self._dimensions
                ):
                    raise (
                        InvalidEmbeddingResponseError(
                            "Titan returned an unexpected embedding dimension."
                        )
                    )

                span.set_attribute(
                    "embedding.returned_dimensions",
                    len(embedding),
                )

                logger.info(
                    "Bedrock embedding request completed",
                    extra={
                        "component": (
                            "TitanEmbeddingProvider"
                        ),
                        "model_id": (
                            self._model_id
                        ),
                        "embedding_dimensions": (
                            len(embedding)
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

                return tuple(
                    float(value)
                    for value in embedding
                )

            except Exception as exc:
                record_exception(span, exc)
                logger.exception(
                    "Bedrock embedding request failed",
                    extra={
                        "component": (
                            "TitanEmbeddingProvider"
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
                raise

    def _invoke_model(
        self,
        text: str,
    ) -> dict[str, Any]:
        request = {
            "inputText": text,
            "dimensions": (
                self._dimensions
            ),
            "normalize": self._normalize,
        }

        return self._client.invoke_model(
            modelId=self._model_id,
            contentType=(
                "application/json"
            ),
            accept="application/json",
            body=json.dumps(request),
        )
