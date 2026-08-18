import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True)
class IntegrationEvent:
    message_id: UUID
    correlation_id: UUID
    event_type: str
    version: int
    occurred_at: str
    payload: dict[str, Any]

    @classmethod
    def create(
        cls,
        *,
        correlation_id: UUID,
        event_type: str,
        payload: dict[str, Any],
        version: int = 1,
    ) -> "IntegrationEvent":
        return cls(
            message_id=uuid4(),
            correlation_id=correlation_id,
            event_type=event_type,
            version=version,
            occurred_at=datetime.now(UTC).isoformat(),
            payload=payload,
        )

    def to_json(self) -> str:
        return json.dumps(
            asdict(self),
            default=str,
            separators=(",", ":"),
        )
