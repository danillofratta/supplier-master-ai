class SupplierApiError(Exception):
    """Base exception for Supplier API errors."""


class SupplierNotFoundError(SupplierApiError):
    """Raised when a supplier does not exist."""