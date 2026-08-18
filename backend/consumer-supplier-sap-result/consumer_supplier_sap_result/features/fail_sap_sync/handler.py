from consumer_supplier_sap_result.features.fail_sap_sync.command import (
    FailSapSyncCommand,
)
from consumer_supplier_sap_result.shared.unit_of_work import (
    SupplierResultUnitOfWork,
)


class FailSapSyncHandler:
    def __init__(
        self,
        unit_of_work: SupplierResultUnitOfWork,
    ) -> None:
        self._uow = unit_of_work

    async def handle(
        self,
        command: FailSapSyncCommand,
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

            workflow.fail(command.reason)

            await uow.workflows.update(workflow)
            await uow.inbox.add(
                command.message_id,
                "supplier.sap-sync.failed.v1",
            )
            await uow.commit()

            return True
