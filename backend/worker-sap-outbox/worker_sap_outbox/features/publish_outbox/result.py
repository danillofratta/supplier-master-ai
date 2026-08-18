from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PublishOutboxResult:
    published: int
    failed: int