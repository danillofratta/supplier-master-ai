from api_supplier.domain.entities.supplier_onboarding_workflow import (
    SupplierOnboardingWorkflow,
)
from api_supplier.domain.enums.supplier_onboarding_status import (
    SupplierOnboardingStatus,
)
from api_supplier.infrastructure.persistence.sqlalchemy.models.supplier_onboarding_workflow_model import (
    SupplierOnboardingWorkflowModel,
)


class SupplierOnboardingWorkflowMapper:
    @staticmethod
    def to_model(
        workflow: SupplierOnboardingWorkflow,
    ) -> SupplierOnboardingWorkflowModel:
        return SupplierOnboardingWorkflowModel(
            workflow_id=workflow.workflow_id,
            supplier_id=workflow.supplier_id,
            status=workflow.status.value,
            service_now_ticket_id=workflow.service_now_ticket_id,
            sap_business_partner_id=workflow.sap_business_partner_id,
            rejection_reason=workflow.rejection_reason,
            failure_reason=workflow.failure_reason,
            created_at=workflow.created_at,
            updated_at=workflow.updated_at,
        )

    @staticmethod
    def to_domain(
        model: SupplierOnboardingWorkflowModel,
    ) -> SupplierOnboardingWorkflow:
        return SupplierOnboardingWorkflow(
            workflow_id=model.workflow_id,
            supplier_id=model.supplier_id,
            status=SupplierOnboardingStatus(model.status),
            service_now_ticket_id=model.service_now_ticket_id,
            sap_business_partner_id=model.sap_business_partner_id,
            rejection_reason=model.rejection_reason,
            failure_reason=model.failure_reason,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
