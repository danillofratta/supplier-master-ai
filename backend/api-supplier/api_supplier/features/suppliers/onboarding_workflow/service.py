from uuid import UUID

from api_supplier.domain.entities.outbox.outbox_message import OutboxMessage
from api_supplier.domain.entities.supplier_onboarding_workflow import (
    SupplierOnboardingWorkflow,
)
from api_supplier.features.suppliers.onboarding_workflow.exceptions import (
    SupplierNotFoundForOnboardingError,
    SupplierOnboardingAlreadyStartedError,
    SupplierOnboardingWorkflowNotFoundError,
)
from api_supplier.features.suppliers.onboarding_workflow.integration_events import (
    SAP_SYNC_REQUESTED_V1,
    build_sap_sync_requested_payload,
)
from api_supplier.shared.messaging.integration_event import IntegrationEvent
from api_supplier.shared.unit_of_work import SupplierUnitOfWork


class SupplierOnboardingWorkflowService:
    def __init__(
        self,
        unit_of_work: SupplierUnitOfWork,
    ) -> None:
        self._unit_of_work = unit_of_work

    async def create_workflow(
        self,
        supplier_id: UUID,
    ) -> SupplierOnboardingWorkflow:
        async with self._unit_of_work as uow:
            supplier = await uow.suppliers.get_by_id(
                supplier_id
            )

            if supplier is None:
                raise SupplierNotFoundForOnboardingError(
                    supplier_id
                )

            latest = (
                await uow.onboarding_workflows
                .get_latest_by_supplier_id(
                    supplier_id
                )
            )

            if (
                latest is not None
                and latest.status.value
                not in {"failed", "rejected"}
            ):
                raise SupplierOnboardingAlreadyStartedError(
                    supplier_id=supplier_id,
                    workflow_id=latest.workflow_id,
                    status=latest.status.value,
                )

            workflow = SupplierOnboardingWorkflow.start(
                supplier_id=supplier.supplier_id
            )
            await uow.onboarding_workflows.add(workflow)
            await uow.commit()
            return workflow

    async def mark_analyzing(
        self,
        workflow_id: UUID,
    ) -> SupplierOnboardingWorkflow:
        workflow = await self._load_workflow(workflow_id)
        workflow.start_analysis()
        return await self._save(workflow)

    async def mark_waiting_review(
        self,
        workflow_id: UUID,
        ticket_id: str,
    ) -> SupplierOnboardingWorkflow:
        workflow = await self._load_workflow(workflow_id)
        workflow.wait_for_human_review(ticket_id)
        return await self._save(workflow)

    async def schedule_sap_sync(
        self,
        workflow_id: UUID,
    ) -> SupplierOnboardingWorkflow:
        """
        Atomically changes the local workflow state and persists the integration
        event. No SAP network call occurs inside this database transaction.
        """
        async with self._unit_of_work as uow:
            workflow = await uow.onboarding_workflows.get_by_id(
                workflow_id
            )
            if workflow is None:
                raise SupplierOnboardingWorkflowNotFoundError(
                    workflow_id
                )

            supplier = await uow.suppliers.get_by_id(
                workflow.supplier_id
            )
            if supplier is None:
                raise SupplierNotFoundForOnboardingError(
                    workflow.supplier_id
                )

            workflow.start_sap_sync()

            integration_event = IntegrationEvent.create(
                correlation_id=workflow.correlation_id,
                event_type=SAP_SYNC_REQUESTED_V1,
                payload=build_sap_sync_requested_payload(
                    supplier=supplier,
                    workflow_id=workflow.workflow_id,
                ),
            )
            outbox_message = OutboxMessage.create(
                message_id=integration_event.message_id,
                event_type=integration_event.event_type,
                payload=integration_event.to_json(),
            )

            await uow.onboarding_workflows.update(workflow)
            await uow.outbox_messages.add(outbox_message)
            await uow.commit()
            return workflow

    async def complete_workflow(
        self,
        workflow_id: UUID,
        business_partner_id: str,
    ) -> SupplierOnboardingWorkflow:
        workflow = await self._load_workflow(workflow_id)
        workflow.complete(business_partner_id)
        return await self._save(workflow)

    async def reject_workflow(
        self,
        workflow_id: UUID,
        reason: str,
    ) -> SupplierOnboardingWorkflow:
        workflow = await self._load_workflow(workflow_id)
        workflow.reject(reason)
        return await self._save(workflow)

    async def fail_workflow(
        self,
        workflow_id: UUID,
        reason: str,
    ) -> SupplierOnboardingWorkflow:
        workflow = await self._load_workflow(workflow_id)
        workflow.fail(reason)
        return await self._save(workflow)

    async def _load_workflow(
        self,
        workflow_id: UUID,
    ) -> SupplierOnboardingWorkflow:
        async with self._unit_of_work as uow:
            workflow = await uow.onboarding_workflows.get_by_id(
                workflow_id
            )
            if workflow is None:
                raise SupplierOnboardingWorkflowNotFoundError(
                    workflow_id
                )
            return workflow

    async def _save(
        self,
        workflow: SupplierOnboardingWorkflow,
    ) -> SupplierOnboardingWorkflow:
        async with self._unit_of_work as uow:
            await uow.onboarding_workflows.update(workflow)
            await uow.commit()
            return workflow
