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
    def _parse(message: dict) -> dict:
        import json

        body = json.loads(message["Body"])
        required = [
            "message_id",
            "correlation_id",
            "event_type",
            "version",
            "occurred_at",
            "payload",
        ]
        missing = [
            field for field in required
            if field not in body
        ]
        if missing:
            raise ValueError(
                f"Invalid integration event. Missing fields: {missing}"
            )
        if not isinstance(body["payload"], dict):
            raise ValueError(
                "Integration event payload must be an object."
            )
        return body

    @staticmethod
    def get_event_type(message: dict) -> str:
        return SqsMessageMapper._parse(message)[
            "event_type"
        ]

    @staticmethod
    def to_complete_command(
        message: dict,
    ) -> CompleteSapSyncCommand:
        body = SqsMessageMapper._parse(message)

        if body["event_type"] != SAP_SYNC_COMPLETED_V1:
            raise ValueError(
                f"Unexpected event type '{body['event_type']}'."
            )

        payload = body["payload"]
        required = [
            "workflow_id",
            "supplier_id",
            "business_partner_id",
        ]
        missing = [
            field for field in required
            if not payload.get(field)
        ]
        if missing:
            raise ValueError(
                f"Invalid SAP completion payload. Missing fields: {missing}"
            )

        return CompleteSapSyncCommand(
            message_id=UUID(body["message_id"]),
            correlation_id=UUID(body["correlation_id"]),
            workflow_id=UUID(payload["workflow_id"]),
            supplier_id=UUID(payload["supplier_id"]),
            business_partner_id=payload[
                "business_partner_id"
            ],
            sap_supplier_id=payload.get(
                "sap_supplier_id"
            ),
        )

    @staticmethod
    def to_fail_command(
        message: dict,
    ) -> FailSapSyncCommand:
        body = SqsMessageMapper._parse(message)

        if body["event_type"] != SAP_SYNC_FAILED_V1:
            raise ValueError(
                f"Unexpected event type '{body['event_type']}'."
            )

        payload = body["payload"]
        required = [
            "workflow_id",
            "supplier_id",
            "reason",
        ]
        missing = [
            field for field in required
            if not payload.get(field)
        ]
        if missing:
            raise ValueError(
                f"Invalid SAP failure payload. Missing fields: {missing}"
            )

        return FailSapSyncCommand(
            message_id=UUID(body["message_id"]),
            correlation_id=UUID(body["correlation_id"]),
            workflow_id=UUID(payload["workflow_id"]),
            supplier_id=UUID(payload["supplier_id"]),
            reason=payload["reason"],
        )
