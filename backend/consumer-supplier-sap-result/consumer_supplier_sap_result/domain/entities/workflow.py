from dataclasses import dataclass
from uuid import UUID

from consumer_supplier_sap_result.domain.enums.status import (
    SupplierOnboardingStatus,
)


@dataclass
class SupplierOnboardingWorkflow:
    workflow_id: UUID
    correlation_id: UUID
    supplier_id: UUID
    status: SupplierOnboardingStatus
    sap_business_partner_id: str | None = None
    failure_reason: str | None = None

    def complete(
        self,
        business_partner_id: str,
    ) -> None:
        if self.status == SupplierOnboardingStatus.COMPLETED:
            return
        if self.status != SupplierOnboardingStatus.SYNCING_TO_SAP:
            raise ValueError(
                f"Cannot complete SAP sync from status '{self.status.value}'."
            )
        self.sap_business_partner_id = business_partner_id
        self.failure_reason = None
        self.status = SupplierOnboardingStatus.COMPLETED

    def fail(
        self,
        reason: str,
    ) -> None:
        if self.status == SupplierOnboardingStatus.FAILED:
            return
        if self.status != SupplierOnboardingStatus.SYNCING_TO_SAP:
            raise ValueError(
                f"Cannot fail SAP sync from status '{self.status.value}'."
            )
        self.failure_reason = reason
        self.status = SupplierOnboardingStatus.FAILED
