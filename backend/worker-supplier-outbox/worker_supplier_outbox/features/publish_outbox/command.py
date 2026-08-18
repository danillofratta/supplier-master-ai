from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class PublishOutboxCommand:
    limit: int = 100
