from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from api_supplier.domain.entities.supplier_onboarding_workflow import (
    SupplierOnboardingWorkflow,
)
from api_supplier.domain.repositories.supplier_onboarding_workflow_repository import (
    SupplierOnboardingWorkflowWriteConflictError,
)
from api_supplier.infrastructure.persistence.sqlalchemy.mappers.supplier_onboarding_workflow_mapper import (
    SupplierOnboardingWorkflowMapper,
)
from api_supplier.infrastructure.persistence.sqlalchemy.models.supplier_onboarding_workflow_model import (
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
        try:
            # Flush here so unique-constraint conflicts are surfaced at the
            # repository boundary while the transaction is still controlled
            # by the Unit of Work.
            await self._session.flush()
        except IntegrityError as exc:
            raise SupplierOnboardingWorkflowWriteConflictError(
                "Supplier onboarding workflow insert conflicted with an existing row."
            ) from exc

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

    async def get_by_idempotency_key(
        self,
        idempotency_key: UUID,
    ) -> SupplierOnboardingWorkflow | None:
        result = await self._session.execute(
            select(SupplierOnboardingWorkflowModel).where(
                SupplierOnboardingWorkflowModel.idempotency_key
                == idempotency_key
            )
        )
        model = result.scalar_one_or_none()
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

    async def get_latest_by_supplier_id(
        self,
        supplier_id: UUID,
    ) -> SupplierOnboardingWorkflow | None:
        result = await self._session.execute(
            select(
                SupplierOnboardingWorkflowModel
            )
            .where(
                SupplierOnboardingWorkflowModel.supplier_id
                == supplier_id
            )
            .order_by(
                SupplierOnboardingWorkflowModel.created_at.desc()
            )
            .limit(1)
        )

        model = result.scalar_one_or_none()

        if model is None:
            return None

        return SupplierOnboardingWorkflowMapper.to_domain(
            model
        )


class InMemorySupplierOnboardingWorkflowRepository:
    def __init__(self) -> None:
        self._workflows: dict[UUID, SupplierOnboardingWorkflow] = {}

    async def add(
        self,
        workflow: SupplierOnboardingWorkflow,
    ) -> None:
        # Mirrors the DB uniqueness guarantee closely enough for unit tests.
        existing = await self.get_by_idempotency_key(
            workflow.idempotency_key
        )
        if existing is not None:
            raise SupplierOnboardingWorkflowWriteConflictError(
                "Idempotency key already exists."
            )
        self._workflows[workflow.workflow_id] = workflow

    async def get_by_id(
        self,
        workflow_id: UUID,
    ) -> SupplierOnboardingWorkflow | None:
        return self._workflows.get(workflow_id)

    async def get_by_idempotency_key(
        self,
        idempotency_key: UUID,
    ) -> SupplierOnboardingWorkflow | None:
        return next(
            (
                workflow
                for workflow in self._workflows.values()
                if workflow.idempotency_key == idempotency_key
            ),
            None,
        )

    async def update(
        self,
        workflow: SupplierOnboardingWorkflow,
    ) -> None:
        self._workflows[workflow.workflow_id] = workflow

    async def get_latest_by_supplier_id(
        self,
        supplier_id: UUID,
    ) -> SupplierOnboardingWorkflow | None:
        workflows = [
            workflow
            for workflow in self._workflows.values()
            if workflow.supplier_id == supplier_id
        ]

        if not workflows:
            return None

        return max(
            workflows,
            key=lambda workflow: workflow.created_at,
        )
