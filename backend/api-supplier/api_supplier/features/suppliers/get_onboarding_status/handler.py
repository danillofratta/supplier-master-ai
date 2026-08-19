from api_supplier.features.suppliers.get_onboarding_status.query import (
    GetSupplierOnboardingQuery,
)
from api_supplier.features.suppliers.get_onboarding_status.result import (
    GetSupplierOnboardingResult,
)
from api_supplier.shared.unit_of_work import (
    SupplierUnitOfWork,
)


class GetSupplierOnboardingHandler:
    def __init__(
        self,
        unit_of_work: SupplierUnitOfWork,
    ) -> None:
        self._unit_of_work = unit_of_work

    async def handle(
        self,
        query: GetSupplierOnboardingQuery,
    ) -> GetSupplierOnboardingResult | None:
        async with self._unit_of_work as uow:
            workflow = (
                await uow.onboarding_workflows
                .get_latest_by_supplier_id(
                    query.supplier_id
                )
            )

        if workflow is None:
            return None

        return GetSupplierOnboardingResult(
            workflow_id=workflow.workflow_id,
            correlation_id=workflow.correlation_id,
            supplier_id=workflow.supplier_id,
            status=workflow.status.value,
            service_now_ticket_id=(
                workflow.service_now_ticket_id
            ),
            sap_business_partner_id=(
                workflow.sap_business_partner_id
            ),
            rejection_reason=workflow.rejection_reason,
            failure_reason=workflow.failure_reason,
            created_at=workflow.created_at,
            updated_at=workflow.updated_at,
        )
