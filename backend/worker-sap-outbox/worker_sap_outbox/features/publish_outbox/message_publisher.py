from typing import Protocol


class MessagePublisher(Protocol):
    async def publish(
            seld,
            *,
            event_type: str,
            payload: str,
            message_id: str,
    ) -> None:
        ...