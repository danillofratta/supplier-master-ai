import json
from uuid import uuid4

from consumer_supplier_sap_result.infrastructure.messaging.sqs_message_mapper import (
    SqsMessageMapper,
)


def test_maps_completed_sap_result_message() -> None:
    workflow_id = uuid4()
    supplier_id = uuid4()
    message_id = uuid4()

    message = {
        "Body": json.dumps({
            "event_id": str(uuid4()),
            "workflow_id": str(workflow_id),
            "supplier_id": str(supplier_id),
            "business_partner_id": "100000001",
            "sap_supplier_id": "200000001",
            "version": 1,
        }),
        "MessageAttributes": {
            "event_type": {
                "StringValue": "supplier.sap-sync.completed.v1",
                "DataType": "String",
            },
            "message_id": {
                "StringValue": str(message_id),
                "DataType": "String",
            },
        },
    }

    command = SqsMessageMapper.to_complete_command(
        message
    )

    assert command.message_id == message_id
    assert command.workflow_id == workflow_id
    assert command.supplier_id == supplier_id
    assert command.business_partner_id == "100000001"
