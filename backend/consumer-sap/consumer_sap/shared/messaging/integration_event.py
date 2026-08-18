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

    @classmethod
    def from_json(
        cls,
        raw: str,
    ) -> "IntegrationEvent":
        data = json.loads(raw)
        required = {
            "message_id",
            "correlation_id",
            "event_type",
            "version",
            "occurred_at",
            "payload",
        }
        missing = sorted(required - data.keys())
        if missing:
            raise ValueError(
                f"Invalid integration event. Missing fields: {missing}"
            )
        if not isinstance(data["payload"], dict):
            raise ValueError("Integration event payload must be an object.")
        return cls(
            message_id=UUID(data["message_id"]),
            correlation_id=UUID(data["correlation_id"]),
            event_type=data["event_type"],
            version=int(data["version"]),
            occurred_at=data["occurred_at"],
            payload=data["payload"],
        )

    def to_json(self) -> str:
        return json.dumps(
            asdict(self),
            default=str,
            separators=(",", ":"),
        )
