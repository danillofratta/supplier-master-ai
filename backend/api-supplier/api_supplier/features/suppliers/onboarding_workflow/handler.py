from api_supplier.domain.enums.supplier_recommended_action import (
    SupplierRecommendedAction,
)
from api_supplier.features.suppliers.analyze.command import (
    AnalyzeSupplierCommand,
)
from api_supplier.features.suppliers.analyze.handler import (
    AnalyzeSupplierHandler,
)
from api_supplier.features.suppliers.onboarding_workflow.command import (
    StartSupplierOnboardingWorkflowCommand,
)
from api_supplier.features.suppliers.onboarding_workflow.result import (
    StartSupplierOnboardingWorkflowResult,
)
from api_supplier.features.suppliers.onboarding_workflow.service import (
    SupplierOnboardingWorkflowService,
)
from api_supplier.features.suppliers.request_review.command import (
    RequestSupplierReviewCommand,
)
from api_supplier.features.suppliers.request_review.handler import (
    RequestSupplierReviewHandler,
)


class StartSupplierOnboardingWorkflowHandler:
    def __init__(
        self,
        analyze_supplier: AnalyzeSupplierHandler,
        request_review: RequestSupplierReviewHandler,
        service: SupplierOnboardingWorkflowService,
    ) -> None:
        self._analyze_supplier = analyze_supplier
        self._request_review = request_review
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
            workflow = await self._service.schedule_sap_sync(
                workflow.workflow_id
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
