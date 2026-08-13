from backend.app.domain.enums.supplier_recommended_action import (
    SupplierRecommendedAction,
)
from backend.app.features.suppliers.analyze.command import (
    AnalyzeSupplierCommand,
)
from backend.app.features.suppliers.analyze.handler import (
    AnalyzeSupplierHandler,
)
from backend.app.features.suppliers.onboarding_workflow.command import (
    StartSupplierOnboardingWorkflowCommand,
)
from backend.app.features.suppliers.onboarding_workflow.result import (
    StartSupplierOnboardingWorkflowResult,
)
from backend.app.features.suppliers.onboarding_workflow.service import (
    SupplierOnboardingWorkflowService,
)
from backend.app.features.suppliers.request_review.command import (
    RequestSupplierReviewCommand,
)
from backend.app.features.suppliers.request_review.handler import (
    RequestSupplierReviewHandler,
)
from backend.app.features.suppliers.sync_to_sap.command import (
    SyncSupplierToSapCommand,
)
from backend.app.features.suppliers.sync_to_sap.handler import (
    SyncSupplierToSapHandler,
)


class StartSupplierOnboardingWorkflowHandler:
    def __init__(
        self,
        analyze_supplier: AnalyzeSupplierHandler,
        request_review: RequestSupplierReviewHandler,
        sync_to_sap: SyncSupplierToSapHandler,
        service: SupplierOnboardingWorkflowService,
    ) -> None:
        self._analyze_supplier = analyze_supplier
        self._request_review = request_review
        self._sync_to_sap = sync_to_sap
        self._service = service

    async def handle(
        self,
        command: StartSupplierOnboardingWorkflowCommand,
    ) -> StartSupplierOnboardingWorkflowResult:
        workflow = await self._service.create_workflow(
            command.supplier_id
        )
        workflow = await self._service.mark_analyzing(
            workflow.workflow_id
        )

        analysis = await self._analyze_supplier.handle(
            AnalyzeSupplierCommand(
                supplier_id=command.supplier_id
            )
        )

        if (
            analysis.recommended_action
            == SupplierRecommendedAction.HUMAN_REVIEW
        ):
            review = await self._request_review.handle(
                RequestSupplierReviewCommand(
                    supplier_id=command.supplier_id,
                    risk_level=analysis.risk_level.value,
                    reason=analysis.summary,
                    policy_ids=analysis.retrieved_policy_ids,
                )
            )
            workflow = await self._service.mark_waiting_review(
                workflow.workflow_id,
                review.ticket_id,
            )

        elif (
            analysis.recommended_action
            == SupplierRecommendedAction.APPROVE
        ):
            workflow = await self._service.mark_syncing_to_sap(
                workflow.workflow_id
            )
            sap = await self._sync_to_sap.handle(
                SyncSupplierToSapCommand(
                    supplier_id=command.supplier_id
                )
            )
            workflow = await self._service.complete_workflow(
                workflow.workflow_id,
                sap.business_partner_id,
            )

        elif (
            analysis.recommended_action
            == SupplierRecommendedAction.REJECT
        ):
            workflow = await self._service.reject_workflow(
                workflow.workflow_id,
                analysis.summary,
            )

        return StartSupplierOnboardingWorkflowResult(
            onboarding_workflow_id=workflow.workflow_id,
            supplier_id=command.supplier_id,
            status=workflow.status,
        )
