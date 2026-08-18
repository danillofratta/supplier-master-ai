import json
from datetime import UTC, datetime
from uuid import uuid4

from consumer_supplier_sap_result.infrastructure.messaging.sqs_message_mapper import (
    SqsMessageMapper,
)


def test_maps_completed_sap_result_message() -> None:
    workflow_id = uuid4()
    supplier_id = uuid4()
    message_id = uuid4()
    correlation_id = uuid4()

    message = {
        "Body": json.dumps({
            "message_id": str(message_id),
            "correlation_id": str(correlation_id),
            "event_type": "supplier.sap-sync.completed.v1",
            "version": 1,
            "occurred_at": datetime.now(UTC).isoformat(),
            "payload": {
                "workflow_id": str(workflow_id),
                "supplier_id": str(supplier_id),
                "business_partner_id": "100000001",
                "sap_supplier_id": "200000001",
            },
        }),
        "MessageAttributes": {},
    }

    command = SqsMessageMapper.to_complete_command(
        message
    )

    assert command.message_id == message_id
    assert command.correlation_id == correlation_id
    assert command.workflow_id == workflow_id
    assert command.supplier_id == supplier_id
    assert command.business_partner_id == "100000001"
