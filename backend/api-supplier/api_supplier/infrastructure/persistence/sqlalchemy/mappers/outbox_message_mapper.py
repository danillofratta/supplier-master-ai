from api_supplier.domain.entities.outbox.outbox_message import OutboxMessage
from api_supplier.infrastructure.persistence.sqlalchemy.models.outbox_message_model import (
    OutboxMessageModel,
)


class OutboxMessageMapper:
    @staticmethod
    def to_model(
        message: OutboxMessage,
    ) -> OutboxMessageModel:
        return OutboxMessageModel(
            message_id=message.message_id,
            event_type=message.event_type,
            payload=message.payload,
            created_at=message.created_at,
            processed_at=message.processed_at,
            attempts=message.attempts,
        )

    @staticmethod
    def to_domain(
        model: OutboxMessageModel,
    ) -> OutboxMessage:
        return OutboxMessage(
            message_id=model.message_id,
            event_type=model.event_type,
            payload=model.payload,
            created_at=model.created_at,
            processed_at=model.processed_at,
            attempts=model.attempts,
        )
