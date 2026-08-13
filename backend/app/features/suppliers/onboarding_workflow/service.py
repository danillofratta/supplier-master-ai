from uuid import UUID

from backend.app.domain.entities.supplier_onboarding_workflow import (
    SupplierOnboardingWorkflow,
)
from backend.app.features.suppliers.onboarding_workflow.exceptions import (
    SupplierNotFoundForOnboardingError,
    SupplierOnboardingWorkflowNotFoundError,
)
from backend.app.shared.unit_of_work import SupplierUnitOfWork


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
            supplier = await uow.suppliers.get_by_id(supplier_id)

            if supplier is None:
                raise SupplierNotFoundForOnboardingError(supplier_id)

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

    async def mark_syncing_to_sap(
        self,
        workflow_id: UUID,
    ) -> SupplierOnboardingWorkflow:
        workflow = await self._load_workflow(workflow_id)
        workflow.start_sap_sync()
        return await self._save(workflow)

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
