from __future__ import annotations

import asyncio
import logging
from time import perf_counter
from typing import Any

from api_supplier.features.policies.ingest.embedding_provider import (
    EmbeddingProvider,
)
from api_supplier.features.suppliers.analyze.policy_context import (
    PolicyContext,
)
from api_supplier.shared.observability import (
    get_tracer,
    record_exception,
)


logger = logging.getLogger(__name__)
tracer = get_tracer("api-supplier")


class OpenSearchPolicyRetriever:
    def __init__(
        self,
        *,
        client: Any,
        embedding_provider: EmbeddingProvider,
        index_name: str,
    ) -> None:
        self._client = client
        self._embedding_provider = (
            embedding_provider
        )
        self._index_name = index_name

    async def retrieve(
        self,
        query: str,
        *,
        limit: int = 5,
    ) -> tuple[PolicyContext, ...]:
        if not query.strip():
            return ()
        if limit <= 0:
            raise ValueError(
                "limit must be greater than zero."
            )

        started = perf_counter()

        with tracer.start_as_current_span(
            "opensearch.policy.retrieve"
        ) as span:
            span.set_attribute(
                "db.system",
                "opensearch",
            )
            span.set_attribute(
                "db.namespace",
                self._index_name,
            )
            span.set_attribute(
                "rag.limit",
                limit,
            )

            try:
                embedding_started = (
                    perf_counter()
                )

                with tracer.start_as_current_span(
                    "embedding.generate"
                ) as embedding_span:
                    query_embedding = (
                        await self
                        ._embedding_provider
                        .generate(query)
                    )
                    embedding_span.set_attribute(
                        "embedding.dimensions",
                        len(query_embedding),
                    )

                logger.info(
                    "policy query embedding generated",
                    extra={
                        "component": (
                            "EmbeddingProvider"
                        ),
                        "duration_ms": round(
                            (
                                perf_counter()
                                - embedding_started
                            )
                            * 1000,
                            2,
                        ),
                        "embedding_dimensions": (
                            len(query_embedding)
                        ),
                    },
                )

                search_started = perf_counter()

                with tracer.start_as_current_span(
                    "opensearch.search"
                ) as search_span:
                    search_span.set_attribute(
                        "db.system",
                        "opensearch",
                    )
                    search_span.set_attribute(
                        "db.namespace",
                        self._index_name,
                    )

                    response = await asyncio.to_thread(
                        self._search_sync,
                        query_embedding,
                        limit,
                    )

                    contexts = self._map_results(
                        response
                    )
                    search_span.set_attribute(
                        "db.response.returned_rows",
                        len(contexts),
                    )

                logger.info(
                    "OpenSearch policy query completed",
                    extra={
                        "component": (
                            "OpenSearchPolicyRetriever"
                        ),
                        "index_name": (
                            self._index_name
                        ),
                        "document_count": (
                            len(contexts)
                        ),
                        "duration_ms": round(
                            (
                                perf_counter()
                                - search_started
                            )
                            * 1000,
                            2,
                        ),
                    },
                )

                span.set_attribute(
                    "rag.document_count",
                    len(contexts),
                )
                span.set_attribute(
                    "app.duration_ms",
                    round(
                        (
                            perf_counter()
                            - started
                        )
                        * 1000,
                        2,
                    ),
                )

                return contexts

            except Exception as exc:
                record_exception(span, exc)
                logger.exception(
                    "OpenSearch policy retrieval failed",
                    extra={
                        "component": (
                            "OpenSearchPolicyRetriever"
                        ),
                        "index_name": (
                            self._index_name
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

    def _search_sync(
        self,
        query_embedding: tuple[
            float,
            ...,
        ],
        limit: int,
    ) -> dict:
        return self._client.search(
            index=self._index_name,
            body={
                "size": limit,
                "_source": {
                    "excludes": ["embedding"],
                },
                "query": {
                    "knn": {
                        "embedding": {
                            "vector": list(
                                query_embedding
                            ),
                            "k": limit,
                        }
                    }
                },
            },
        )

    @staticmethod
    def _map_results(
        response: dict,
    ) -> tuple[PolicyContext, ...]:
        hits = (
            response.get(
                "hits",
                {},
            ).get(
                "hits",
                [],
            )
        )
        contexts: list[
            PolicyContext
        ] = []

        for hit in hits:
            source = hit.get(
                "_source",
                {},
            )
            contexts.append(
                PolicyContext(
                    document_id=str(
                        source["document_id"]
                    ),
                    chunk_id=str(
                        source["chunk_id"]
                    ),
                    title=str(
                        source["title"]
                    ),
                    content=str(
                        source["content"]
                    ),
                    policy_type=str(
                        source["policy_type"]
                    ),
                    version=str(
                        source["version"]
                    ),
                    effective_date=str(
                        source[
                            "effective_date"
                        ]
                    ),
                    score=float(
                        hit.get(
                            "_score",
                            0.0,
                        )
                    ),
                )
            )

        return tuple(contexts)
