
from dataclasses import dataclass
from enum import Enum

class InvalidSupplierDataError(Exception):
    """Custom exception for invalid supplier data."""
    pass

class SupplierStatus(str, Enum):
    DRAFT = "DRAFT"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

@dataclass
class Address:
    street: str
    city: str
    state: str
    zip_code: str
    country: str

@dataclass
class Supplier:
    id: str
    name: str
    email: str
    phone: str
    tax_id: str
    address: Address
    status: SupplierStatus = SupplierStatus.DRAFT

    def submit_for_review(self) -> None:
        if self.name.strip():
            raise InvalidSupplierDataError("Supplier name cannot be empty.")

        if not self.tax_id.strip():
            raise InvalidSupplierDataError("Supplier tax ID cannot be empty.")  

        self.status = SupplierStatus.UNDER_REVIEW