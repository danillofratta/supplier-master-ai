from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.domain.entities.supplier_onboarding_workflow import (
    SupplierOnboardingWorkflow,
)
from backend.app.infrastructure.persistence.sqlalchemy.mappers.supplier_onboarding_workflow_mapper import (
    SupplierOnboardingWorkflowMapper,
)
from backend.app.infrastructure.persistence.sqlalchemy.models.supplier_onboarding_workflow_model import (
    SupplierOnboardingWorkflowModel,
)


class PostgreSQLSupplierOnboardingWorkflowRepository:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

    async def add(
        self,
        workflow: SupplierOnboardingWorkflow,
    ) -> None:
        self._session.add(
            SupplierOnboardingWorkflowMapper.to_model(workflow)
        )

    async def get_by_id(
        self,
        workflow_id: UUID,
    ) -> SupplierOnboardingWorkflow | None:
        model = await self._session.get(
            SupplierOnboardingWorkflowModel,
            workflow_id,
        )
        if model is None:
            return None
        return SupplierOnboardingWorkflowMapper.to_domain(model)

    async def update(
        self,
        workflow: SupplierOnboardingWorkflow,
    ) -> None:
        model = await self._session.get(
            SupplierOnboardingWorkflowModel,
            workflow.workflow_id,
        )
        if model is None:
            self._session.add(
                SupplierOnboardingWorkflowMapper.to_model(workflow)
            )
            return

        model.status = workflow.status.value
        model.service_now_ticket_id = workflow.service_now_ticket_id
        model.sap_business_partner_id = workflow.sap_business_partner_id
        model.rejection_reason = workflow.rejection_reason
        model.failure_reason = workflow.failure_reason
        model.updated_at = workflow.updated_at


class InMemorySupplierOnboardingWorkflowRepository:
    def __init__(self) -> None:
        self._workflows: dict[UUID, SupplierOnboardingWorkflow] = {}

    async def add(
        self,
        workflow: SupplierOnboardingWorkflow,
    ) -> None:
        self._workflows[workflow.workflow_id] = workflow

    async def get_by_id(
        self,
        workflow_id: UUID,
    ) -> SupplierOnboardingWorkflow | None:
        return self._workflows.get(workflow_id)

    async def update(
        self,
        workflow: SupplierOnboardingWorkflow,
    ) -> None:
        self._workflows[workflow.workflow_id] = workflow
