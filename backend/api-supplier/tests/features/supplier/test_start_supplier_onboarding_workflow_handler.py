import json
from uuid import uuid4

import pytest

from api_supplier.domain.entities.address import Address
from api_supplier.domain.entities.supplier import Supplier
from api_supplier.domain.enums.supplier_onboarding_status import (
    SupplierOnboardingStatus,
)
from api_supplier.domain.enums.supplier_recommended_action import (
    SupplierRecommendedAction,
)
from api_supplier.domain.enums.supplier_risk_level import SupplierRiskLevel
from api_supplier.features.suppliers.analyze.supplier_analyzer import (
    SupplierAnalysisResult,
)
from api_supplier.features.suppliers.onboarding_workflow.command import (
    StartSupplierOnboardingWorkflowCommand,
)
from api_supplier.features.suppliers.onboarding_workflow.exceptions import (
    SupplierOnboardingAlreadyStartedError,
    SupplierOnboardingIdempotencyConflictError,
)
from api_supplier.features.suppliers.onboarding_workflow.handler import (
    StartSupplierOnboardingWorkflowHandler,
)
from api_supplier.features.suppliers.onboarding_workflow.integration_events import (
    SAP_SYNC_REQUESTED_V1,
)
from api_supplier.features.suppliers.onboarding_workflow.service import (
    SupplierOnboardingWorkflowService,
)
from api_supplier.features.suppliers.request_review.result import (
    RequestSupplierReviewResult,
)
from api_supplier.infrastructure.persistence.in_memory_unit_of_work import (
    InMemorySupplierUnitOfWork,
)


class FakeAnalyzeSupplierHandler:
    def __init__(self, action: SupplierRecommendedAction) -> None:
        self._action = action
        self.calls = 0

    async def handle(self, command) -> SupplierAnalysisResult:
        self.calls += 1
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


def build_supplier(name: str = "ACME") -> Supplier:
    return Supplier(
        supplier_id=uuid4(),
        name=name,
        email=f"contact@{name.lower()}.test",
        phone="11999999999",
        tax_id=str(uuid4().int)[:14],
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

    analyzer = FakeAnalyzeSupplierHandler(action)
    review = FakeRequestSupplierReviewHandler()

    handler = StartSupplierOnboardingWorkflowHandler(
        analyze_supplier=analyzer,
        request_review=review,
        service=SupplierOnboardingWorkflowService(uow),
    )
    return supplier, uow, handler, analyzer, review


@pytest.mark.asyncio
async def test_human_review_waits_for_servicenow() -> None:
    supplier, _, handler, _, review = await build_handler(
        SupplierRecommendedAction.HUMAN_REVIEW
    )

    result = await handler.handle(
        StartSupplierOnboardingWorkflowCommand(
            supplier_id=supplier.supplier_id,
            idempotency_key=uuid4(),
        )
    )

    assert result.status == SupplierOnboardingStatus.WAITING_HUMAN_REVIEW
    assert review.calls == 1


@pytest.mark.asyncio
async def test_approve_schedules_sap_sync_in_outbox() -> None:
    supplier, uow, handler, _, review = await build_handler(
        SupplierRecommendedAction.APPROVE
    )

    result = await handler.handle(
        StartSupplierOnboardingWorkflowCommand(
            supplier_id=supplier.supplier_id,
            idempotency_key=uuid4(),
        )
    )

    assert result.status == SupplierOnboardingStatus.SYNCING_TO_SAP
    assert review.calls == 0

    pending = await uow.outbox_messages.get_pending_messages()
    assert len(pending) == 1
    assert pending[0].event_type == SAP_SYNC_REQUESTED_V1

    event = json.loads(pending[0].payload)
    assert event["message_id"] == str(pending[0].message_id)
    assert event["event_type"] == SAP_SYNC_REQUESTED_V1
    assert event["correlation_id"]
    assert event["payload"]["workflow_id"] == str(
        result.onboarding_workflow_id
    )
    assert event["payload"]["supplier_id"] == str(
        supplier.supplier_id
    )
    assert event["payload"]["tax_id"] == supplier.tax_id


@pytest.mark.asyncio
async def test_reject_does_not_schedule_external_work() -> None:
    supplier, uow, handler, _, review = await build_handler(
        SupplierRecommendedAction.REJECT
    )

    result = await handler.handle(
        StartSupplierOnboardingWorkflowCommand(
            supplier_id=supplier.supplier_id,
            idempotency_key=uuid4(),
        )
    )

    assert result.status == SupplierOnboardingStatus.REJECTED
    assert review.calls == 0
    assert await uow.outbox_messages.get_pending_messages() == ()


@pytest.mark.asyncio
async def test_same_idempotency_key_replays_existing_workflow_without_side_effects() -> None:
    supplier, uow, handler, analyzer, review = await build_handler(
        SupplierRecommendedAction.HUMAN_REVIEW
    )
    idempotency_key = uuid4()
    command = StartSupplierOnboardingWorkflowCommand(
        supplier_id=supplier.supplier_id,
        idempotency_key=idempotency_key,
    )

    first = await handler.handle(command)
    second = await handler.handle(command)

    assert second.onboarding_workflow_id == first.onboarding_workflow_id
    assert second.status == first.status
    assert analyzer.calls == 1
    assert review.calls == 1
    existing = await uow.onboarding_workflows.get_by_idempotency_key(
        idempotency_key
    )
    assert existing is not None
    assert existing.workflow_id == first.onboarding_workflow_id


@pytest.mark.asyncio
async def test_same_idempotency_key_cannot_be_reused_for_another_supplier() -> None:
    supplier, uow, handler, _, _ = await build_handler(
        SupplierRecommendedAction.HUMAN_REVIEW
    )
    second_supplier = build_supplier("OTHER")
    await uow.suppliers.add(second_supplier)
    idempotency_key = uuid4()

    await handler.handle(
        StartSupplierOnboardingWorkflowCommand(
            supplier_id=supplier.supplier_id,
            idempotency_key=idempotency_key,
        )
    )

    with pytest.raises(SupplierOnboardingIdempotencyConflictError):
        await handler.handle(
            StartSupplierOnboardingWorkflowCommand(
                supplier_id=second_supplier.supplier_id,
                idempotency_key=idempotency_key,
            )
        )


@pytest.mark.asyncio
async def test_cannot_start_second_active_onboarding_with_different_key() -> None:
    supplier, _, handler, _, _ = await build_handler(
        SupplierRecommendedAction.HUMAN_REVIEW
    )

    await handler.handle(
        StartSupplierOnboardingWorkflowCommand(
            supplier_id=supplier.supplier_id,
            idempotency_key=uuid4(),
        )
    )

    with pytest.raises(SupplierOnboardingAlreadyStartedError):
        await handler.handle(
            StartSupplierOnboardingWorkflowCommand(
                supplier_id=supplier.supplier_id,
                idempotency_key=uuid4(),
            )
        )
