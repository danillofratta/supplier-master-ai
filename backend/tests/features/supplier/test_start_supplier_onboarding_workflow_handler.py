from uuid import uuid4

import pytest

from backend.app.domain.entities.address import Address
from backend.app.domain.entities.supplier import Supplier
from backend.app.domain.enums.supplier_onboarding_status import (
    SupplierOnboardingStatus,
)
from backend.app.domain.enums.supplier_recommended_action import (
    SupplierRecommendedAction,
)
from backend.app.domain.enums.supplier_risk_level import SupplierRiskLevel
from backend.app.features.suppliers.analyze.supplier_analyzer import (
    SupplierAnalysisResult,
)
from backend.app.features.suppliers.onboarding_workflow.command import (
    StartSupplierOnboardingWorkflowCommand,
)
from backend.app.features.suppliers.onboarding_workflow.handler import (
    StartSupplierOnboardingWorkflowHandler,
)
from backend.app.features.suppliers.onboarding_workflow.service import (
    SupplierOnboardingWorkflowService,
)
from backend.app.features.suppliers.request_review.result import (
    RequestSupplierReviewResult,
)
from backend.app.features.suppliers.sync_to_sap.result import (
    SyncSupplierToSapResult,
)
from backend.app.infrastructure.persistence.in_memory_unit_of_work import (
    InMemorySupplierUnitOfWork,
)


class FakeAnalyzeSupplierHandler:
    def __init__(self, action: SupplierRecommendedAction) -> None:
        self._action = action

    async def handle(self, command) -> SupplierAnalysisResult:
        return SupplierAnalysisResult(
            risk_level=SupplierRiskLevel.HIGH
            if self._action == SupplierRecommendedAction.HUMAN_REVIEW
            else SupplierRiskLevel.LOW,
            recommended_action=self._action,
            missing_documents=(),
            policy_violations=(),
            summary="Workflow analysis.",
            confidence=0.95,
            retrieved_policy_ids=("policy-001",),
        )


class FakeRequestSupplierReviewHandler:
    def __init__(self) -> None:
        self.calls = 0

    async def handle(self, command) -> RequestSupplierReviewResult:
        self.calls += 1
        return RequestSupplierReviewResult(
            supplier_id=command.supplier_id,
            ticket_id="sys-001",
            ticket_number="RITM0001001",
            status="OPEN",
        )


class FakeSyncSupplierToSapHandler:
    def __init__(self) -> None:
        self.calls = 0

    async def handle(self, command) -> SyncSupplierToSapResult:
        self.calls += 1
        return SyncSupplierToSapResult(
            supplier_id=command.supplier_id,
            business_partner_id="100000001",
            sap_supplier_id="200000001",
            already_existed=False,
        )


def build_supplier() -> Supplier:
    return Supplier(
        supplier_id=uuid4(),
        name="ACME",
        email="contact@acme.com",
        phone="11999999999",
        tax_id="12345678000190",
        address=Address(
            street="Main Street",
            city="Sao Paulo",
            state="SP",
            zip_code="01000-000",
            country="Brazil",
        ),
    )


async def build_handler(action: SupplierRecommendedAction):
    supplier = build_supplier()
    uow = InMemorySupplierUnitOfWork()
    await uow.suppliers.add(supplier)

    review = FakeRequestSupplierReviewHandler()
    sap = FakeSyncSupplierToSapHandler()

    handler = StartSupplierOnboardingWorkflowHandler(
        analyze_supplier=FakeAnalyzeSupplierHandler(action),
        request_review=review,
        sync_to_sap=sap,
        service=SupplierOnboardingWorkflowService(uow),
    )
    return supplier, uow, handler, review, sap


@pytest.mark.asyncio
async def test_human_review_waits_for_servicenow() -> None:
    supplier, uow, handler, review, sap = await build_handler(
        SupplierRecommendedAction.HUMAN_REVIEW
    )

    result = await handler.handle(
        StartSupplierOnboardingWorkflowCommand(
            supplier_id=supplier.supplier_id
        )
    )

    assert result.status == SupplierOnboardingStatus.WAITING_HUMAN_REVIEW
    assert review.calls == 1
    assert sap.calls == 0

    workflow = await uow.onboarding_workflows.get_by_id(
        result.onboarding_workflow_id
    )
    assert workflow is not None
    assert workflow.service_now_ticket_id == "sys-001"


@pytest.mark.asyncio
async def test_approve_syncs_to_sap_and_completes() -> None:
    supplier, uow, handler, review, sap = await build_handler(
        SupplierRecommendedAction.APPROVE
    )

    result = await handler.handle(
        StartSupplierOnboardingWorkflowCommand(
            supplier_id=supplier.supplier_id
        )
    )

    assert result.status == SupplierOnboardingStatus.COMPLETED
    assert review.calls == 0
    assert sap.calls == 1

    workflow = await uow.onboarding_workflows.get_by_id(
        result.onboarding_workflow_id
    )
    assert workflow is not None
    assert workflow.sap_business_partner_id == "100000001"


@pytest.mark.asyncio
async def test_reject_does_not_call_external_systems() -> None:
    supplier, uow, handler, review, sap = await build_handler(
        SupplierRecommendedAction.REJECT
    )

    result = await handler.handle(
        StartSupplierOnboardingWorkflowCommand(
            supplier_id=supplier.supplier_id
        )
    )

    assert result.status == SupplierOnboardingStatus.REJECTED
    assert review.calls == 0
    assert sap.calls == 0
