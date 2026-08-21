import logging
from time import perf_counter

from api_supplier.features.policies.ingest.command import (
    IngestPolicyCommand,
)
from api_supplier.features.policies.ingest.document_chunker import (
    DocumentChunker,
)
from api_supplier.features.policies.ingest.embedding_provider import (
    EmbeddingProvider,
)
from api_supplier.features.policies.ingest.indexed_policy_chunk import (
    IndexedPolicyChunk,
)
from api_supplier.features.policies.ingest.policy_index import (
    PolicyIndex,
)
from api_supplier.features.policies.ingest.result import (
    IngestPolicyResult,
)
from api_supplier.shared.observability import (
    get_tracer,
    record_exception,
)


logger = logging.getLogger(__name__)
tracer = get_tracer("api-supplier")


class IngestPolicyHandler:
    def __init__(
        self,
        chunker: DocumentChunker,
        embedding_provider: EmbeddingProvider,
        policy_index: PolicyIndex,
    ) -> None:
        self._chunker = chunker
        self._embedding_provider = (
            embedding_provider
        )
        self._policy_index = policy_index

    async def handle(
        self,
        command: IngestPolicyCommand,
    ) -> IngestPolicyResult:
        started = perf_counter()

        with tracer.start_as_current_span(
            "feature.IngestPolicy"
        ) as span:
            span.set_attribute(
                "app.feature",
                "IngestPolicy",
            )
            span.set_attribute(
                "policy.document_id",
                command.document_id,
            )
            span.set_attribute(
                "policy.version",
                command.version,
            )

            logger.info(
                "policy ingestion started",
                extra={
                    "feature": "IngestPolicy",
                    "component": "PolicyIngest",
                    "document_id": command.document_id,
                    "policy_version": command.version,
                },
            )

            try:
                chunks = self._chunker.split(
                    command
                )

                if not chunks:
                    raise EmptyPolicyContentError(
                        command.document_id
                    )

                indexed_chunks: list[
                    IndexedPolicyChunk
                ] = []

                # Build the replacement completely before deleting the
                # existing version. This avoids losing a valid indexed
                # document if embedding generation fails midway.
                for chunk in chunks:
                    embedding = (
                        await self._embedding_provider
                        .generate(
                            chunk.content
                        )
                    )

                    indexed_chunks.append(
                        IndexedPolicyChunk(
                            chunk=chunk,
                            embedding=embedding,
                        )
                    )

                indexed_chunks_tuple = tuple(
                    indexed_chunks
                )

                await self._policy_index.delete_document(
                    document_id=command.document_id,
                    version=command.version,
                )
                await self._policy_index.upsert(
                    indexed_chunks_tuple
                )

                result = IngestPolicyResult(
                    document_id=command.document_id,
                    chunks_indexed=len(
                        indexed_chunks_tuple
                    ),
                    embedding_dimensions=(
                        self._embedding_provider
                        .dimensions
                    ),
                )

                span.set_attribute(
                    "policy.chunks_indexed",
                    result.chunks_indexed,
                )
                span.set_attribute(
                    "embedding.dimensions",
                    result.embedding_dimensions,
                )

                logger.info(
                    "policy ingestion completed",
                    extra={
                        "feature": "IngestPolicy",
                        "component": "PolicyIngest",
                        "document_id": (
                            result.document_id
                        ),
                        "chunks_indexed": (
                            result.chunks_indexed
                        ),
                        "embedding_dimensions": (
                            result
                            .embedding_dimensions
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

            except Exception as exc:
                record_exception(span, exc)
                logger.exception(
                    "policy ingestion failed",
                    extra={
                        "feature": "IngestPolicy",
                        "component": "PolicyIngest",
                        "document_id": command.document_id,
                        "policy_version": command.version,
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


class EmptyPolicyContentError(Exception):
    def __init__(
        self,
        document_id: str,
    ) -> None:
        self.document_id = document_id
        super().__init__(
            f"Policy '{document_id}' has no content."
        )
