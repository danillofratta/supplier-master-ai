from typing import Protocol


class EmbeddingProvider(Protocol):
    @property
    def dimensions(self) -> int:
        ...

    async def generate(
        self,
        text: str,
    ) -> tuple[float, ...]:
        ...
