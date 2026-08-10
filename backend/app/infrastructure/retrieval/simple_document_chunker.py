from backend.app.features.policies.ingest.command import IngestPolicyCommand
from backend.app.features.policies.ingest.policy_chunk import PolicyChunk


class SimpleDocumentChunker:
    def __init__(
        self,
        *,
        max_characters: int = 1200,
        overlap_characters: int = 200,
    ) -> None:
        if max_characters <= 0:
            raise ValueError("max_characters must be greater than zero.")

        if overlap_characters < 0:
            raise ValueError("overlap_characters cannot be negative.")

        if overlap_characters >= max_characters:
            raise ValueError(
                "overlap_characters must be smaller than max_characters."
            )

        self._max_characters = max_characters
        self._overlap_characters = overlap_characters

    def split(
        self,
        command: IngestPolicyCommand,
    ) -> tuple[PolicyChunk, ...]:
        normalized_content = self._normalize_text(command.content)

        if not normalized_content:
            return ()

        texts = self._split_text(normalized_content)

        return tuple(
            PolicyChunk(
                document_id=command.document_id,
                chunk_id=f"{command.document_id}:{position:04d}",
                title=command.title,
                content=text,
                policy_type=command.policy_type,
                version=command.version,
                effective_date=command.effective_date,
                position=position,
            )
            for position, text in enumerate(texts)
        )

    @staticmethod
    def _normalize_text(content: str) -> str:
        paragraphs = (
            paragraph.strip()
            for paragraph in content.splitlines()
        )
        return "\n".join(
            paragraph
            for paragraph in paragraphs
            if paragraph
        )

    def _split_text(self, content: str) -> list[str]:
        chunks: list[str] = []
        start = 0

        while start < len(content):
            end = min(start + self._max_characters, len(content))
            chunk = content[start:end].strip()

            if chunk:
                chunks.append(chunk)

            if end == len(content):
                break

            start = end - self._overlap_characters

        return chunks
