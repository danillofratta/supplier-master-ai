from api_supplier.features.policies.ingest.command import IngestPolicyCommand
from api_supplier.features.policies.ingest.document_chunker import DocumentChunker
from api_supplier.features.policies.ingest.embedding_provider import EmbeddingProvider
from api_supplier.features.policies.ingest.indexed_policy_chunk import (
    IndexedPolicyChunk,
)
from api_supplier.features.policies.ingest.policy_index import PolicyIndex
from api_supplier.features.policies.ingest.result import IngestPolicyResult


class IngestPolicyHandler:
    def __init__(
        self,
        chunker: DocumentChunker,
        embedding_provider: EmbeddingProvider,
        policy_index: PolicyIndex,
    ) -> None:
        self._chunker = chunker
        self._embedding_provider = embedding_provider
        self._policy_index = policy_index

    async def handle(
        self,
        command: IngestPolicyCommand,
    ) -> IngestPolicyResult:
        chunks = self._chunker.split(command)

        if not chunks:
            raise EmptyPolicyContentError(
                command.document_id
            )

        await self._policy_index.delete_document(
            document_id=command.document_id,
            version=command.version,
        )

        indexed_chunks: list[IndexedPolicyChunk] = []

        for chunk in chunks:
            embedding = await self._embedding_provider.generate(
                chunk.content
            )

            indexed_chunks.append(
                IndexedPolicyChunk(
                    chunk=chunk,
                    embedding=embedding,
                )
            )

        indexed_chunks_tuple = tuple(indexed_chunks)

        await self._policy_index.upsert(
            indexed_chunks_tuple
        )

        return IngestPolicyResult(
            document_id=command.document_id,
            chunks_indexed=len(indexed_chunks_tuple),
            embedding_dimensions=(
                self._embedding_provider.dimensions
            ),
        )


class EmptyPolicyContentError(Exception):
    def __init__(self, document_id: str) -> None:
        self.document_id = document_id
        super().__init__(f"Policy '{document_id}' has no content.")
