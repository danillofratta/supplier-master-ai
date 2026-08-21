from datetime import UTC, datetime

from consumer_supplier_sap_result.domain.entities.workflow import (
    SupplierOnboardingWorkflow,
)
from consumer_supplier_sap_result.domain.enums.status import (
    SupplierOnboardingStatus,
)
from consumer_supplier_sap_result.infrastructure.persistence.sqlalchemy.models import (
    InboxMessageModel,
    WorkflowModel,
)


class PostgreSQLWorkflowRepository:
    def __init__(self, session) -> None:
        self._session = session

    async def get_by_id(
        self,
        workflow_id,
    ) -> SupplierOnboardingWorkflow | None:
        model = await self._session.get(
            WorkflowModel,
            workflow_id,
        )

        if model is None:
            return None

        return SupplierOnboardingWorkflow(
            workflow_id=model.workflow_id,
            correlation_id=model.correlation_id,
            supplier_id=model.supplier_id,
            status=SupplierOnboardingStatus(model.status),
            sap_business_partner_id=(
                model.sap_business_partner_id
            ),
            failure_reason=model.failure_reason,
            updated_at=model.updated_at,
        )

    async def update(
        self,
        workflow: SupplierOnboardingWorkflow,
    ) -> None:
        model = await self._session.get(
            WorkflowModel,
            workflow.workflow_id,
        )

        if model is None:
            raise ValueError(
                f"Workflow '{workflow.workflow_id}' not found."
            )

        model.status = workflow.status.value
        model.sap_business_partner_id = (
            workflow.sap_business_partner_id
        )
        model.failure_reason = workflow.failure_reason
        model.updated_at = workflow.updated_at


class PostgreSQLInboxRepository:
    def __init__(self, session) -> None:
        self._session = session

    async def exists(
        self,
        message_id,
    ) -> bool:
        return (
            await self._session.get(
                InboxMessageModel,
                message_id,
            )
            is not None
        )

    async def add(
        self,
        message_id,
        event_type,
    ) -> None:
        self._session.add(
            InboxMessageModel(
                message_id=message_id,
                event_type=event_type,
                processed_at=datetime.now(UTC),
            )
        )
