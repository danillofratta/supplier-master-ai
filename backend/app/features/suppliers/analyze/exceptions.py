from uuid import UUID


class SupplierNotFoundError(Exception):
    def __init__(self, supplier_id: UUID) -> None:
        self.supplier_id = supplier_id
        super().__init__(f"Supplier '{supplier_id}' was not found.")

class SupplierAnalysisProviderError(Exception):
    """Raised when the configured AI provider cannot execute the analysis."""


class InvalidSupplierAnalysisResponseError(Exception):
    """Raised when the AI provider responds with an invalid payload."""

