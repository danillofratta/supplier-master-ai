from uuid import uuid4

import pytest

from api_supplier.domain.entities.supplier_onboarding_workflow import (
    SupplierOnboardingWorkflow,
)
from api_supplier.domain.enums.supplier_onboarding_status import (
    SupplierOnboardingStatus,
)
from api_supplier.features.suppliers.onboarding_workflow.exceptions import (
    InvalidSupplierOnboardingTransitionError,
)


def start_workflow() -> SupplierOnboardingWorkflow:
    return SupplierOnboardingWorkflow.start(
        supplier_id=uuid4(),
        idempotency_key=uuid4(),
    )


def test_workflow_stores_idempotency_key() -> None:
    idempotency_key = uuid4()
    workflow = SupplierOnboardingWorkflow.start(
        supplier_id=uuid4(),
        idempotency_key=idempotency_key,
    )

    assert workflow.idempotency_key == idempotency_key


def test_workflow_human_review_transition() -> None:
    workflow = start_workflow()

    workflow.start_analysis()
    workflow.wait_for_human_review("sys-001")

    assert workflow.status == SupplierOnboardingStatus.WAITING_HUMAN_REVIEW
    assert workflow.service_now_ticket_id == "sys-001"


def test_workflow_can_complete_after_sap_sync() -> None:
    workflow = start_workflow()

    workflow.start_analysis()
    workflow.start_sap_sync()
    workflow.complete("100000001")

    assert workflow.status == SupplierOnboardingStatus.COMPLETED
    assert workflow.sap_business_partner_id == "100000001"


def test_invalid_transition_is_rejected() -> None:
    workflow = start_workflow()

    with pytest.raises(InvalidSupplierOnboardingTransitionError):
        workflow.complete("100000001")
