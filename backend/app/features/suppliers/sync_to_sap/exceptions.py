from uuid import UUID


class SupplierNotFoundForSapSyncError(Exception):
    def __init__(self, supplier_id: UUID) -> None:
        self.supplier_id = supplier_id
        super().__init__(
            f"Supplier '{supplier_id}' was not found for SAP synchronization."
        )


class SapSupplierProviderError(Exception):
    pass
