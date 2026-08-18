import json
from uuid import uuid4

import pytest

from consumer_sap.features.sync_supplier.command import (
    SyncSupplierCommand,
)
from consumer_sap.features.sync_supplier.contracts import (
    AddressDto,
)
from consumer_sap.features.sync_supplier.handler import (
    SyncSupplierHandler,
)
from consumer_sap.infrastructure.integrations.sap.fake_sap_gateway import (
    FakeSapGateway,
)
from consumer_sap.infrastructure.persistence.in_memory import (
    InMemorySapIntegrationUnitOfWork,
)
from consumer_sap.features.sync_supplier.sap_gateway import (
    SapSupplierDto,
)


def command(message_id=None):
    return SyncSupplierCommand(
        message_id=message_id or uuid4(),
        correlation_id=uuid4(),
        workflow_id=uuid4(),
        supplier_id=uuid4(),
        name="ACME",
        email="a@a.com",
        phone="1",
        tax_id="12.345.678/0001-90",
        address=AddressDto(
            "Street",
            "City",
            "SP",
            "01000-000",
            "Brazil",
        ),
    )


@pytest.mark.asyncio
async def test_creates_operation_inbox_and_outbox():
    uow = InMemorySapIntegrationUnitOfWork()
    gateway = FakeSapGateway()
    cmd = command()

    result = await SyncSupplierHandler(
        uow,
        gateway,
    ).handle(cmd)

    assert result is not None
    assert gateway.create_calls == 1
    assert len(uow.inbox.items) == 1
    assert len(uow.operations.items) == 1
    assert len(uow.outbox_messages.items) == 1

    operation = next(iter(uow.operations.items.values()))
    assert operation.correlation_id == cmd.correlation_id

    outbox = next(iter(uow.outbox_messages.items.values()))
    event = json.loads(outbox.payload)
    assert event["message_id"] == str(outbox.message_id)
    assert event["correlation_id"] == str(cmd.correlation_id)
    assert event["event_type"] == "supplier.sap-sync.completed.v1"


@pytest.mark.asyncio
async def test_duplicate_message_is_idempotent():
    uow = InMemorySapIntegrationUnitOfWork()
    gateway = FakeSapGateway()
    cmd = command()
    handler = SyncSupplierHandler(uow, gateway)

    await handler.handle(cmd)
    second = await handler.handle(cmd)

    assert second is None
    assert gateway.create_calls == 1


@pytest.mark.asyncio
async def test_reconciles_existing_supplier_before_create():
    uow = InMemorySapIntegrationUnitOfWork()
    gateway = FakeSapGateway()
    cmd = command()

    gateway.seed(
        cmd.tax_id,
        SapSupplierDto(
            "100000777",
            "200000777",
        ),
    )

    result = await SyncSupplierHandler(
        uow,
        gateway,
    ).handle(cmd)

    assert result.already_existed is True
    assert gateway.create_calls == 0
