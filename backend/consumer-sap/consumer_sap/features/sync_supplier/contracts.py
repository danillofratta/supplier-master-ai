from dataclasses import dataclass


SAP_SYNC_REQUESTED_V1 = "supplier.sap-sync.requested.v1"
SAP_SYNC_COMPLETED_V1 = "supplier.sap-sync.completed.v1"
SAP_SYNC_FAILED_V1 = "supplier.sap-sync.failed.v1"


@dataclass(frozen=True, slots=True)
class AddressDto:
    street: str
    city: str
    state: str
    zip_code: str
    country: str


def build_sap_sync_completed_payload(
    *,
    workflow_id,
    supplier_id,
    business_partner_id: str,
    sap_supplier_id: str | None,
) -> dict:
    return {
        "workflow_id": str(workflow_id),
        "supplier_id": str(supplier_id),
        "business_partner_id": business_partner_id,
        "sap_supplier_id": sap_supplier_id,
    }


def build_sap_sync_failed_payload(
    *,
    workflow_id,
    supplier_id,
    reason: str,
) -> dict:
    return {
        "workflow_id": str(workflow_id),
        "supplier_id": str(supplier_id),
        "reason": reason,
    }
