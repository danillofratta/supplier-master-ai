import json
from uuid import UUID

from consumer_supplier_sap_result.features.complete_sap_sync.command import (
    CompleteSapSyncCommand,
)
from consumer_supplier_sap_result.features.fail_sap_sync.command import (
    FailSapSyncCommand,
)


SAP_SYNC_COMPLETED_V1 = "supplier.sap-sync.completed.v1"
SAP_SYNC_FAILED_V1 = "supplier.sap-sync.failed.v1"


class SqsMessageMapper:
    @staticmethod
    def get_event_type(
        message: dict,
    ) -> str:
        attributes = message.get(
            "MessageAttributes",
            {},
        )

        event_type = attributes.get(
            "event_type",
            {},
        ).get("StringValue")

        if not event_type:
            raise ValueError(
                "SQS message does not contain event_type."
            )

        return event_type

    @staticmethod
    def _get_message_id(
        message: dict,
    ) -> UUID:
        attributes = message.get(
            "MessageAttributes",
            {},
        )

        value = attributes.get(
            "message_id",
            {},
        ).get("StringValue")

        if not value:
            # Fallback to event_id in the integration payload.
            body = json.loads(message["Body"])
            value = body.get("event_id")

        if not value:
            raise ValueError(
                "SQS message does not contain a message identifier."
            )

        return UUID(value)

    @staticmethod
    def to_complete_command(
        message: dict,
    ) -> CompleteSapSyncCommand:
        body = json.loads(message["Body"])

        required = [
            "workflow_id",
            "supplier_id",
            "business_partner_id",
        ]
        missing = [
            field
            for field in required
            if not body.get(field)
        ]
        if missing:
            raise ValueError(
                f"Invalid SAP completion message. Missing fields: {missing}"
            )

        return CompleteSapSyncCommand(
            message_id=SqsMessageMapper._get_message_id(
                message
            ),
            workflow_id=UUID(body["workflow_id"]),
            supplier_id=UUID(body["supplier_id"]),
            business_partner_id=body[
                "business_partner_id"
            ],
            sap_supplier_id=body.get(
                "sap_supplier_id"
            ),
        )

    @staticmethod
    def to_fail_command(
        message: dict,
    ) -> FailSapSyncCommand:
        body = json.loads(message["Body"])

        required = [
            "workflow_id",
            "supplier_id",
            "reason",
        ]
        missing = [
            field
            for field in required
            if not body.get(field)
        ]
        if missing:
            raise ValueError(
                f"Invalid SAP failure message. Missing fields: {missing}"
            )

        return FailSapSyncCommand(
            message_id=SqsMessageMapper._get_message_id(
                message
            ),
            workflow_id=UUID(body["workflow_id"]),
            supplier_id=UUID(body["supplier_id"]),
            reason=body["reason"],
        )
