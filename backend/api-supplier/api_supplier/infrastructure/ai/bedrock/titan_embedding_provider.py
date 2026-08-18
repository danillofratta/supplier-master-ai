import asyncio
import json
from typing import Any

from api_supplier.features.policies.ingest.embedding_provider import (
    EmbeddingProvider,
)


class InvalidEmbeddingResponseError(Exception):
    pass


class TitanEmbeddingProvider(EmbeddingProvider):
    def __init__(
        self,
        *,
        region_name: str,
        model_id: str = "amazon.titan-embed-text-v2:0",
        dimensions: int = 1024,
        normalize: bool = True,
    ) -> None:
        if dimensions not in {256, 512, 1024}:
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
            raise ValueError("Embedding text cannot be empty.")

        response = await asyncio.to_thread(
            self._invoke_model,
            text,
        )

        payload = json.loads(response["body"].read())
        embedding = payload.get("embedding")

        if not isinstance(embedding, list):
            raise InvalidEmbeddingResponseError(
                "Titan did not return a valid embedding."
            )

        if len(embedding) != self._dimensions:
            raise InvalidEmbeddingResponseError(
                "Titan returned an unexpected embedding dimension."
            )

        return tuple(float(value) for value in embedding)

    def _invoke_model(
        self,
        text: str,
    ) -> dict[str, Any]:
        request = {
            "inputText": text,
            "dimensions": self._dimensions,
            "normalize": self._normalize,
        }

        return self._client.invoke_model(
            modelId=self._model_id,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(request),
        )
