class SupplierAlreadyExistsError(Exception):
    """Raised when a supplier with the same business tax ID already exists."""

    def __init__(self, tax_id: str) -> None:
        self.tax_id = tax_id
        super().__init__(f"Supplier with tax ID '{tax_id}' already exists.")
