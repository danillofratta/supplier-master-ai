from uuid import uuid4

import pytest

from api_supplier.domain.entities.address import Address
from api_supplier.domain.entities.supplier import Supplier
from api_supplier.domain.enums.supplier_status import SupplierStatus
from api_supplier.domain.exceptions import DomainError

def create_supplier() -> Supplier:
    return Supplier(
        supplier_id=uuid4(),
        name="Test Supplier",
        email="test@test.com",
        phone="1234567890",
        tax_id="123456789",
        address=Address(
            street="123 Test St",
            city="Test City",
            state="Test State",
            zip_code="12345",
            country="Test Country",
        ),
    )

def test_supplier_can_be_submitted_for_review() -> None:
    supplier = create_supplier()
    supplier.submit_for_review()
    assert supplier.status == SupplierStatus.UNDER_REVIEW

def test_approved_supplier_cannot_be_submitted_again() -> None:
    supplier = create_supplier()
    supplier.status = SupplierStatus.APPROVED

    with pytest.raises(DomainError):
        supplier.submit_for_review()