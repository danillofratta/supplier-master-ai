from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID

from consumer_supplier_sap_result.domain.enums.status import (
    SupplierOnboardingStatus,
)


def utc_now() -> datetime:
    return datetime.now(UTC)


@dataclass
class SupplierOnboardingWorkflow:
    workflow_id: UUID
    correlation_id: UUID
    supplier_id: UUID
    status: SupplierOnboardingStatus
    sap_business_partner_id: str | None = None
    failure_reason: str | None = None
    updated_at: datetime = field(
        default_factory=utc_now
    )

    def complete(
        self,
        business_partner_id: str,
    ) -> None:
        if self.status == SupplierOnboardingStatus.COMPLETED:
            return

        if (
            self.status
            != SupplierOnboardingStatus.SYNCING_TO_SAP
        ):
            raise ValueError(
                "Cannot complete SAP sync from status "
                f"'{self.status.value}'."
            )

        self.sap_business_partner_id = (
            business_partner_id
        )
        self.failure_reason = None
        self.status = (
            SupplierOnboardingStatus.COMPLETED
        )
        self.updated_at = utc_now()

    def fail(
        self,
        reason: str,
    ) -> None:
        if self.status == SupplierOnboardingStatus.FAILED:
            return

        if (
            self.status
            != SupplierOnboardingStatus.SYNCING_TO_SAP
        ):
            raise ValueError(
                "Cannot fail SAP sync from status "
                f"'{self.status.value}'."
            )

        self.failure_reason = reason
        self.status = SupplierOnboardingStatus.FAILED
        self.updated_at = utc_now()
