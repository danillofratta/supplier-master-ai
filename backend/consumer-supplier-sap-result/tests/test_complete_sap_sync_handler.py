from uuid import uuid4

import pytest

from consumer_supplier_sap_result.domain.entities.workflow import (
    SupplierOnboardingWorkflow,
)
from consumer_supplier_sap_result.domain.enums.status import (
    SupplierOnboardingStatus,
)
from consumer_supplier_sap_result.features.complete_sap_sync.command import (
    CompleteSapSyncCommand,
)
from consumer_supplier_sap_result.features.complete_sap_sync.handler import (
    CompleteSapSyncHandler,
)
from consumer_supplier_sap_result.infrastructure.persistence.in_memory import (
    InMemorySupplierResultUnitOfWork,
)


@pytest.mark.asyncio
async def test_completion_updates_supplier_workflow_and_inbox():
    uow = InMemorySupplierResultUnitOfWork()
    correlation_id = uuid4()
    workflow = SupplierOnboardingWorkflow(
        workflow_id=uuid4(),
        correlation_id=correlation_id,
        supplier_id=uuid4(),
        status=SupplierOnboardingStatus.SYNCING_TO_SAP,
    )
    await uow.workflows.add(workflow)
    previous_updated_at = workflow.updated_at

    cmd = CompleteSapSyncCommand(
        message_id=uuid4(),
        correlation_id=correlation_id,
        workflow_id=workflow.workflow_id,
        supplier_id=workflow.supplier_id,
        business_partner_id="100000001",
        sap_supplier_id="200000001",
    )

    await CompleteSapSyncHandler(uow).handle(cmd)

    stored = await uow.workflows.get_by_id(
        workflow.workflow_id
    )
    assert stored.status == SupplierOnboardingStatus.COMPLETED
    assert stored.sap_business_partner_id == "100000001"
    assert stored.updated_at >= previous_updated_at
    assert await uow.inbox.exists(cmd.message_id)


@pytest.mark.asyncio
async def test_duplicate_result_is_ignored():
    uow = InMemorySupplierResultUnitOfWork()
    correlation_id = uuid4()
    workflow = SupplierOnboardingWorkflow(
        workflow_id=uuid4(),
        correlation_id=correlation_id,
        supplier_id=uuid4(),
        status=SupplierOnboardingStatus.SYNCING_TO_SAP,
    )
    await uow.workflows.add(workflow)

    cmd = CompleteSapSyncCommand(
        message_id=uuid4(),
        correlation_id=correlation_id,
        workflow_id=workflow.workflow_id,
        supplier_id=workflow.supplier_id,
        business_partner_id="100000001",
    )

    handler = CompleteSapSyncHandler(uow)
    await handler.handle(cmd)
    await handler.handle(cmd)

    assert len(uow.inbox.items) == 1
