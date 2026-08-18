from consumer_supplier_sap_result.features.complete_sap_sync.command import (
    CompleteSapSyncCommand,
)
from consumer_supplier_sap_result.shared.unit_of_work import (
    SupplierResultUnitOfWork,
)


class CompleteSapSyncHandler:
    def __init__(
        self,
        unit_of_work: SupplierResultUnitOfWork,
    ) -> None:
        self._uow = unit_of_work

    async def handle(
        self,
        command: CompleteSapSyncCommand,
    ) -> bool:
        async with self._uow as uow:
            if await uow.inbox.exists(command.message_id):
                return False

            workflow = await uow.workflows.get_by_id(
                command.workflow_id
            )
            if workflow is None:
                raise ValueError(
                    f"Workflow '{command.workflow_id}' not found."
                )

            if workflow.correlation_id != command.correlation_id:
                raise ValueError(
                    "Correlation ID does not match the supplier workflow."
                )

            if workflow.supplier_id != command.supplier_id:
                raise ValueError(
                    "Supplier ID does not match the supplier workflow."
                )

            workflow.complete(
                command.business_partner_id
            )

            await uow.workflows.update(workflow)
            await uow.inbox.add(
                command.message_id,
                "supplier.sap-sync.completed.v1",
            )
            await uow.commit()
            return True
