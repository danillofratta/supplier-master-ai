from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4

from backend.app.domain.enums.supplier_onboarding_status import (
    SupplierOnboardingStatus,
)
from backend.app.features.suppliers.onboarding_workflow.exceptions import (
    InvalidSupplierOnboardingTransitionError,
)


def utc_now() -> datetime:
    return datetime.now(UTC)


@dataclass
class SupplierOnboardingWorkflow:
    supplier_id: UUID
    workflow_id: UUID
    status: SupplierOnboardingStatus
    service_now_ticket_id: str | None = None
    sap_business_partner_id: str | None = None
    rejection_reason: str | None = None
    failure_reason: str | None = None
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    @classmethod
    def start(
        cls,
        supplier_id: UUID,
    ) -> "SupplierOnboardingWorkflow":
        return cls(
            supplier_id=supplier_id,
            workflow_id=uuid4(),
            status=SupplierOnboardingStatus.PENDING,
        )

    def start_analysis(self) -> None:
        self._ensure_status(SupplierOnboardingStatus.PENDING)
        self.status = SupplierOnboardingStatus.ANALYZING
        self._touch()

    def wait_for_human_review(
        self,
        ticket_id: str,
    ) -> None:
        self._ensure_status(SupplierOnboardingStatus.ANALYZING)
        self.service_now_ticket_id = ticket_id
        self.status = SupplierOnboardingStatus.WAITING_HUMAN_REVIEW
        self._touch()

    def start_sap_sync(self) -> None:
        if self.status not in {
            SupplierOnboardingStatus.ANALYZING,
            SupplierOnboardingStatus.WAITING_HUMAN_REVIEW,
        }:
            raise InvalidSupplierOnboardingTransitionError(
                f"Cannot start SAP sync from status '{self.status.value}'."
            )

        self.status = SupplierOnboardingStatus.SYNCING_TO_SAP
        self._touch()

    def complete(
        self,
        business_partner_id: str,
    ) -> None:
        self._ensure_status(SupplierOnboardingStatus.SYNCING_TO_SAP)
        self.sap_business_partner_id = business_partner_id
        self.status = SupplierOnboardingStatus.COMPLETED
        self._touch()

    def reject(
        self,
        reason: str,
    ) -> None:
        if self.status not in {
            SupplierOnboardingStatus.ANALYZING,
            SupplierOnboardingStatus.WAITING_HUMAN_REVIEW,
        }:
            raise InvalidSupplierOnboardingTransitionError(
                f"Cannot reject onboarding from status '{self.status.value}'."
            )

        self.rejection_reason = reason
        self.status = SupplierOnboardingStatus.REJECTED
        self._touch()

    def fail(
        self,
        reason: str,
    ) -> None:
        if self.status in {
            SupplierOnboardingStatus.COMPLETED,
            SupplierOnboardingStatus.REJECTED,
        }:
            raise InvalidSupplierOnboardingTransitionError(
                f"Cannot fail onboarding from terminal status '{self.status.value}'."
            )

        self.failure_reason = reason
        self.status = SupplierOnboardingStatus.FAILED
        self._touch()

    def _ensure_status(
        self,
        expected: SupplierOnboardingStatus,
    ) -> None:
        if self.status != expected:
            raise InvalidSupplierOnboardingTransitionError(
                f"Expected status '{expected.value}' but was '{self.status.value}'."
            )

    def _touch(self) -> None:
        self.updated_at = utc_now()
