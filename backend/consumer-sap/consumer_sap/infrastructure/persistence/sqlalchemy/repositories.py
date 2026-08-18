from datetime import UTC, datetime

from sqlalchemy import select

from consumer_sap.domain.entities.sap_sync_operation import SapSyncOperation
from consumer_sap.domain.enums.sap_sync_status import SapSyncStatus
from consumer_sap.infrastructure.persistence.sqlalchemy.models import (
    InboxMessageModel,
    OutboxMessageModel,
    SapSyncOperationModel,
)


class PostgreSQLInboxRepository:
    def __init__(self, session) -> None:
        self._session = session

    async def exists(self, message_id) -> bool:
        return (
            await self._session.get(
                InboxMessageModel,
                message_id,
            )
            is not None
        )

    async def add(
        self,
        message_id,
        event_type,
    ) -> None:
        self._session.add(
            InboxMessageModel(
                message_id=message_id,
                event_type=event_type,
                processed_at=datetime.now(UTC),
            )
        )


class PostgreSQLOperationRepository:
    def __init__(self, session) -> None:
        self._session = session

    async def get_by_message_id(
        self,
        message_id,
    ) -> SapSyncOperation | None:
        result = await self._session.execute(
            select(SapSyncOperationModel).where(
                SapSyncOperationModel.message_id
                == message_id
            )
        )
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return SapSyncOperation(
            operation_id=model.operation_id,
            message_id=model.message_id,
            workflow_id=model.workflow_id,
            supplier_id=model.supplier_id,
            tax_id=model.tax_id,
            status=SapSyncStatus(model.status),
            business_partner_id=model.business_partner_id,
            sap_supplier_id=model.sap_supplier_id,
            attempts=model.attempts or 0,
            failure_reason=model.failure_reason,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def add(
        self,
        operation: SapSyncOperation,
    ) -> None:
        self._session.add(
            SapSyncOperationModel(
                operation_id=operation.operation_id,
                message_id=operation.message_id,
                workflow_id=operation.workflow_id,
                supplier_id=operation.supplier_id,
                tax_id=operation.tax_id,
                status=operation.status.value,
                business_partner_id=(
                    operation.business_partner_id
                ),
                sap_supplier_id=operation.sap_supplier_id,
                attempts=operation.attempts,
                failure_reason=operation.failure_reason,
                created_at=operation.created_at,
                updated_at=operation.updated_at,
            )
        )

    async def update(
        self,
        operation: SapSyncOperation,
    ) -> None:
        model = await self._session.get(
            SapSyncOperationModel,
            operation.operation_id,
        )

        if model is None:
            await self.add(operation)
            return

        model.status = operation.status.value
        model.business_partner_id = (
            operation.business_partner_id
        )
        model.sap_supplier_id = operation.sap_supplier_id
        model.attempts = operation.attempts
        model.failure_reason = operation.failure_reason
        model.updated_at = operation.updated_at


class PostgreSQLOutboxRepository:
    def __init__(self, session) -> None:
        self._session = session

    async def add(
        self,
        message,
    ) -> None:
        self._session.add(
            OutboxMessageModel(
                message_id=message.message_id,
                event_type=message.event_type,
                payload=message.payload,
                created_at=message.created_at,
                processed_at=message.processed_at,
                attempts=message.attempts,
            )
        )

        # Forces INSERT errors to surface here instead of being hidden until
        # a later operation. The transaction is still committed by the UoW.
        await self._session.flush()
