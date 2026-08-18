import json
from dataclasses import dataclass
from uuid import UUID


SAP_SYNC_COMPLETED_V1 = "supplier.sap-sync.completed.v1"
SAP_SYNC_FAILED_V1 = "supplier.sap-sync.failed.v1"


@dataclass(frozen=True, slots=True)
class SapSyncCompletedV1:
    event_id: UUID
    workflow_id: UUID
    supplier_id: UUID
    business_partner_id: str
    sap_supplier_id: str | None
    version: int

    @classmethod
    def from_json(
        cls,
        payload: str,
    ) -> "SapSyncCompletedV1":
        data = json.loads(payload)
        return cls(
            event_id=UUID(data["event_id"]),
            workflow_id=UUID(data["workflow_id"]),
            supplier_id=UUID(data["supplier_id"]),
            business_partner_id=data["business_partner_id"],
            sap_supplier_id=data.get("sap_supplier_id"),
            version=int(data["version"]),
        )


@dataclass(frozen=True, slots=True)
class SapSyncFailedV1:
    event_id: UUID
    workflow_id: UUID
    supplier_id: UUID
    reason: str
    version: int

    @classmethod
    def from_json(
        cls,
        payload: str,
    ) -> "SapSyncFailedV1":
        data = json.loads(payload)
        return cls(
            event_id=UUID(data["event_id"]),
            workflow_id=UUID(data["workflow_id"]),
            supplier_id=UUID(data["supplier_id"]),
            reason=data["reason"],
            version=int(data["version"]),
        )
