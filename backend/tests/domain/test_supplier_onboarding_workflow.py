from uuid import uuid4

import pytest

from backend.app.domain.entities.supplier_onboarding_workflow import (
    SupplierOnboardingWorkflow,
)
from backend.app.domain.enums.supplier_onboarding_status import (
    SupplierOnboardingStatus,
)
from backend.app.features.suppliers.onboarding_workflow.exceptions import (
    InvalidSupplierOnboardingTransitionError,
)


def test_workflow_human_review_transition() -> None:
    workflow = SupplierOnboardingWorkflow.start(uuid4())

    workflow.start_analysis()
    workflow.wait_for_human_review("sys-001")

    assert workflow.status == SupplierOnboardingStatus.WAITING_HUMAN_REVIEW
    assert workflow.service_now_ticket_id == "sys-001"


def test_workflow_can_complete_after_sap_sync() -> None:
    workflow = SupplierOnboardingWorkflow.start(uuid4())

    workflow.start_analysis()
    workflow.start_sap_sync()
    workflow.complete("100000001")

    assert workflow.status == SupplierOnboardingStatus.COMPLETED
    assert workflow.sap_business_partner_id == "100000001"


def test_invalid_transition_is_rejected() -> None:
    workflow = SupplierOnboardingWorkflow.start(uuid4())

    with pytest.raises(InvalidSupplierOnboardingTransitionError):
        workflow.complete("100000001")
