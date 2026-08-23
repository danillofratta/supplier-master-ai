class SupplierApiError(Exception):
    """Base exception for errors communicating with Supplier API."""


class ApiNotFoundError(SupplierApiError):
    """Raised when the Supplier API returns HTTP 404."""


class SupplierNotFoundError(Exception):
    """Raised when a supplier does not exist."""


class OnboardingNotFoundError(Exception):
    """Raised when an onboarding workflow does not exist."""

class ConfirmationRequiredError(Exception):
    """Raised when a mutating MCP operation was not explicitly confirmed."""    