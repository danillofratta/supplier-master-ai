from api_supplier.domain.entities.supplier import Supplier


SAP_SYNC_REQUESTED_V1 = "supplier.sap-sync.requested.v1"


def build_sap_sync_requested_payload(
    supplier: Supplier,
    workflow_id,
) -> dict:
    return {
        "workflow_id": str(workflow_id),
        "supplier_id": str(supplier.supplier_id),
        "name": supplier.name,
        "email": supplier.email,
        "phone": supplier.phone,
        "tax_id": supplier.tax_id,
        "address": {
            "street": supplier.address.street,
            "city": supplier.address.city,
            "state": supplier.address.state,
            "zip_code": supplier.address.zip_code,
            "country": supplier.address.country,
        },
    }
