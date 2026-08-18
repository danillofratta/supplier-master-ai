from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

@dataclass
class OutboxMessage:
    message_id: UUID
    event_type: str
    payload: str
    created_at: datetime
    processed_at: datetime | None = None
    attempts: int = 0

    def register_attempt(self) -> None:
        self.attempts += 1

    def mark_processed(self, processed_at: datetime) -> None:
        self.processed_at = processed_at
