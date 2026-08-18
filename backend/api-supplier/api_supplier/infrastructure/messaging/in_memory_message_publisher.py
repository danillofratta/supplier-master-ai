from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PublishedMessage:
    event_type: str
    payload: str
    message_id: str


class InMemoryMessagePublisher:
    def __init__(self) -> None:
        self.messages: list[PublishedMessage] = []

    async def publish(
        self,
        *,
        event_type: str,
        payload: str,
        message_id: str,
    ) -> None:
        self.messages.append(
            PublishedMessage(
                event_type=event_type,
                payload=payload,
                message_id=message_id,
            )
        )
