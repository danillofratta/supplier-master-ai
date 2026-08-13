import re

from backend.app.features.policies.ingest.command import (
    IngestPolicyCommand,
)
from backend.app.features.policies.ingest.policy_chunk import (
    PolicyChunk,
)


class SemanticDocumentChunker:
    def __init__(
        self,
        *,
        max_characters: int = 220,
        overlap_sentences: int = 1,
    ) -> None:
        if max_characters <= 0:
            raise ValueError(
                "max_characters must be greater than zero."
            )

        if overlap_sentences < 0:
            raise ValueError(
                "overlap_sentences cannot be negative."
            )

        self._max_characters = max_characters
        self._overlap_sentences = overlap_sentences

    def split(
        self,
        command: IngestPolicyCommand,
    ) -> tuple[PolicyChunk, ...]:
        sentences = self._split_sentences(
            command.content
        )

        if not sentences:
            return ()

        chunk_texts: list[str] = []
        current_sentences: list[str] = []

        for sentence in sentences:
            candidate = " ".join(
                [*current_sentences, sentence]
            )

            if (
                current_sentences
                and len(candidate) > self._max_characters
            ):
                chunk_texts.append(
                    " ".join(current_sentences)
                )

                overlap = (
                    current_sentences[
                        -self._overlap_sentences:
                    ]
                    if self._overlap_sentences
                    else []
                )

                current_sentences = [
                    *overlap,
                    sentence,
                ]
            else:
                current_sentences.append(sentence)

        if current_sentences:
            chunk_texts.append(
                " ".join(current_sentences)
            )

        return tuple(
            PolicyChunk(
                document_id=command.document_id,
                chunk_id=(
                    f"{command.document_id}:{position:04d}"
                ),
                title=command.title,
                content=content,
                policy_type=command.policy_type,
                version=command.version,
                effective_date=command.effective_date,
                position=position,
            )
            for position, content
            in enumerate(chunk_texts)
        )

    @staticmethod
    def _split_sentences(
        content: str,
    ) -> list[str]:
        normalized = " ".join(
            content.split()
        )

        return [
            sentence.strip()
            for sentence in re.split(
                r"(?<=[.!?])\s+",
                normalized,
            )
            if sentence.strip()
        ]