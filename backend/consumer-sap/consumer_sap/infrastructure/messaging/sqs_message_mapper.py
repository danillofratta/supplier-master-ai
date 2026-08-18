import json
from uuid import UUID

from consumer_sap.features.sync_supplier.command import (
    SyncSupplierCommand,
)
from consumer_sap.features.sync_supplier.contracts import (
    AddressDto,
)


class SqsMessageMapper:
    @staticmethod
    def to_sync_supplier_command(
        message: dict,
    ) -> SyncSupplierCommand:
        body = json.loads(message["Body"])

        attributes = message.get(
            "MessageAttributes",
            {},
        )

        message_id = attributes.get(
            "message_id",
            {},
        ).get("StringValue")

        if not message_id:
            raise ValueError(
                "SQS message does not contain message_id."
            )

        return SyncSupplierCommand(
            message_id=UUID(message_id),
            workflow_id=UUID(body["workflow_id"]),
            supplier_id=UUID(body["supplier_id"]),
            name=body["name"],
            email=body["email"],
            phone=body["phone"],
            tax_id=body["tax_id"],
            address=AddressDto(
                street=body["address"]["street"],
                city=body["address"]["city"],
                state=body["address"]["state"],
                zip_code=body["address"]["zip_code"],
                country=body["address"]["country"],
            ),
        )