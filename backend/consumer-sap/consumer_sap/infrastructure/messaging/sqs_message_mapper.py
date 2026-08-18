from uuid import UUID

from consumer_sap.features.sync_supplier.command import (
    SyncSupplierCommand,
)
from consumer_sap.features.sync_supplier.contracts import (
    AddressDto,
    SAP_SYNC_REQUESTED_V1,
)
from consumer_sap.shared.messaging.integration_event import (
    IntegrationEvent,
)


class SqsMessageMapper:
    @staticmethod
    def to_sync_supplier_command(
        message: dict,
    ) -> SyncSupplierCommand:
        event = IntegrationEvent.from_json(
            message["Body"]
        )

        if event.event_type != SAP_SYNC_REQUESTED_V1:
            raise ValueError(
                f"Unsupported event '{event.event_type}'."
            )

        payload = event.payload
        required = [
            "workflow_id",
            "supplier_id",
            "name",
            "email",
            "phone",
            "tax_id",
            "address",
        ]
        missing = [
            field for field in required
            if field not in payload
        ]
        if missing:
            raise ValueError(
                f"Invalid SAP sync request. Missing fields: {missing}"
            )

        address = payload["address"]
        address_required = [
            "street",
            "city",
            "state",
            "zip_code",
            "country",
        ]
        missing_address = [
            field for field in address_required
            if field not in address
        ]
        if missing_address:
            raise ValueError(
                "Invalid supplier address. "
                f"Missing fields: {missing_address}"
            )

        return SyncSupplierCommand(
            message_id=event.message_id,
            correlation_id=event.correlation_id,
            workflow_id=UUID(payload["workflow_id"]),
            supplier_id=UUID(payload["supplier_id"]),
            name=payload["name"],
            email=payload["email"],
            phone=payload["phone"],
            tax_id=payload["tax_id"],
            address=AddressDto(
                street=address["street"],
                city=address["city"],
                state=address["state"],
                zip_code=address["zip_code"],
                country=address["country"],
            ),
        )
