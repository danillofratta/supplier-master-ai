from api_supplier.domain.entities.supplier_onboarding_workflow import (
    SupplierOnboardingWorkflow,
)
from api_supplier.domain.enums.supplier_onboarding_status import (
    SupplierOnboardingStatus,
)
from api_supplier.features.suppliers.onboarding_workflow.exceptions import (
    SupplierOnboardingForSupplierNotFoundError,
)
from api_supplier.features.suppliers.onboarding_workflow.service import (
    SupplierOnboardingWorkflowService,
)
from api_supplier.features.suppliers.review_decision.command import (
    DecideSupplierReviewCommand,
)
from api_supplier.shared.unit_of_work import (
    SupplierUnitOfWork,
)


class DecideSupplierReviewHandler:
    def __init__(
        self,
        unit_of_work: SupplierUnitOfWork,
        service: SupplierOnboardingWorkflowService,
    ) -> None:
        self._unit_of_work = unit_of_work
        self._service = service

    async def handle(
        self,
        command: DecideSupplierReviewCommand,
    ) -> SupplierOnboardingWorkflow:
        async with self._unit_of_work as uow:
            workflow = (
                await uow.onboarding_workflows
                .get_latest_by_supplier_id(
                    command.supplier_id
                )
            )

        if workflow is None:
            raise SupplierOnboardingForSupplierNotFoundError(
                command.supplier_id
            )

        if (
            workflow.status
            != SupplierOnboardingStatus.WAITING_HUMAN_REVIEW
        ):
            raise ValueError(
                "Supplier onboarding is not waiting for human review."
            )

        if command.decision == "approve":
            return await self._service.schedule_sap_sync(
                workflow.workflow_id
            )

        return await self._service.reject_workflow(
            workflow.workflow_id,
            command.reason
            or "Rejected during human review.",
        )
