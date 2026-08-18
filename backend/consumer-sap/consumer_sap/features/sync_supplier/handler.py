from consumer_sap.domain.entities.outbox_message import (
    OutboxMessage,
)
from consumer_sap.domain.entities.sap_sync_operation import (
    SapSyncOperation,
)
from consumer_sap.features.sync_supplier.command import (
    SyncSupplierCommand,
)
from consumer_sap.features.sync_supplier.contracts import (
    SAP_SYNC_COMPLETED_V1,
    build_sap_sync_completed_payload,
)
from consumer_sap.features.sync_supplier.result import (
    SyncSupplierResult,
)
from consumer_sap.features.sync_supplier.sap_gateway import (
    SapGateway,
)
from consumer_sap.shared.messaging.integration_event import (
    IntegrationEvent,
)
from consumer_sap.shared.unit_of_work import (
    SapIntegrationUnitOfWork,
)


class SyncSupplierHandler:
    def __init__(
        self,
        unit_of_work: SapIntegrationUnitOfWork,
        sap_gateway: SapGateway,
    ) -> None:
        self._uow = unit_of_work
        self._sap = sap_gateway

    async def handle(
        self,
        command: SyncSupplierCommand,
    ) -> SyncSupplierResult | None:
        async with self._uow as uow:
            if await uow.inbox.exists(command.message_id):
                return None

            operation = await uow.operations.get_by_message_id(
                command.message_id
            )

            if operation is None:
                operation = SapSyncOperation.start(
                    message_id=command.message_id,
                    correlation_id=command.correlation_id,
                    workflow_id=command.workflow_id,
                    supplier_id=command.supplier_id,
                    tax_id=command.tax_id,
                )
                await uow.operations.add(operation)

            operation.begin()
            await uow.operations.update(operation)
            await uow.commit()

        existing = await self._sap.find_by_tax_id(
            command.tax_id
        )
        already_existed = existing is not None
        reference = (
            existing
            or await self._sap.create_supplier(command)
        )

        result_event = IntegrationEvent.create(
            correlation_id=command.correlation_id,
            event_type=SAP_SYNC_COMPLETED_V1,
            payload=build_sap_sync_completed_payload(
                workflow_id=command.workflow_id,
                supplier_id=command.supplier_id,
                business_partner_id=(
                    reference.business_partner_id
                ),
                sap_supplier_id=reference.supplier_id,
            ),
        )

        outbox_message = OutboxMessage.create(
            message_id=result_event.message_id,
            event_type=result_event.event_type,
            payload=result_event.to_json(),
        )

        async with self._uow as uow:
            operation = await uow.operations.get_by_message_id(
                command.message_id
            )

            if operation is None:
                raise RuntimeError(
                    "SAP sync operation disappeared."
                )

            operation.complete(
                reference.business_partner_id,
                reference.supplier_id,
            )

            await uow.operations.update(operation)
            await uow.inbox.add(
                command.message_id,
                "supplier.sap-sync.requested.v1",
            )
            await uow.outbox_messages.add(outbox_message)
            await uow.commit()

        return SyncSupplierResult(
            business_partner_id=(
                reference.business_partner_id
            ),
            sap_supplier_id=reference.supplier_id,
            already_existed=already_existed,
        )
