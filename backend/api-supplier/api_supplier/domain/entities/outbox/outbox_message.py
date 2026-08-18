from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4


def utc_now() -> datetime:
    return datetime.now(UTC)


@dataclass
class OutboxMessage:
    message_id: UUID
    event_type: str
    payload: str
    created_at: datetime = field(default_factory=utc_now)
    processed_at: datetime | None = None
    attempts: int = 0

    @classmethod
    def create(
        cls,
        *,
        event_type: str,
        payload: str,
        message_id: UUID | None = None,
    ) -> "OutboxMessage":
        return cls(
            message_id=message_id or uuid4(),
            event_type=event_type,
            payload=payload,
        )

    def mark_processed(self) -> None:
        self.processed_at = utc_now()

    def register_attempt(self) -> None:
        self.attempts = (self.attempts or 0) + 1
