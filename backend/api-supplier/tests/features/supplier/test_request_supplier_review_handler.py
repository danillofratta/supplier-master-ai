from uuid import uuid4

import pytest

from api_supplier.domain.entities.address import Address
from api_supplier.domain.entities.supplier import Supplier
from api_supplier.features.suppliers.request_review.command import (
    RequestSupplierReviewCommand,
)
from api_supplier.features.suppliers.request_review.exceptions import (
    SupplierNotFoundForReviewError,
)
from api_supplier.features.suppliers.request_review.handler import (
    RequestSupplierReviewHandler,
)
from api_supplier.infrastructure.integrations.servicenow.fake_servicenow_gateway import (
    FakeServiceNowGateway,
)
from api_supplier.infrastructure.persistence.in_memory_unit_of_work import (
    InMemorySupplierUnitOfWork,
)


def build_supplier() -> Supplier:
    return Supplier(
        supplier_id=uuid4(),
        name="ACME Supplies",
        email="contact@acme.com",
        phone="11999999999",
        tax_id="12.345.678/0001-90",
        address=Address(
            street="Main Street",
            city="Sao Paulo",
            state="SP",
            zip_code="01000-000",
            country="Brazil",
        ),
    )


@pytest.mark.asyncio
async def test_human_review_creates_servicenow_ticket() -> None:
    supplier = build_supplier()
    uow = InMemorySupplierUnitOfWork()
    await uow.suppliers.add(supplier)
    servicenow_gateway = FakeServiceNowGateway()

    handler = RequestSupplierReviewHandler(
        unit_of_work=uow,
        servicenow_gateway=servicenow_gateway,
    )

    result = await handler.handle(
        RequestSupplierReviewCommand(
            supplier_id=supplier.supplier_id,
            risk_level="high",
            reason="High-risk supplier requires human review.",
            policy_ids=("supplier-onboarding-001",),
        )
    )

    assert result.supplier_id == supplier.supplier_id
    assert result.ticket_id == "sys-001"
    assert result.ticket_number == "RITM0001001"
    assert result.status == "OPEN"
    assert len(servicenow_gateway.created_requests) == 1

    request = servicenow_gateway.created_requests[0]
    assert request.supplier_id == supplier.supplier_id
    assert request.risk_level == "high"
    assert request.policy_ids == ("supplier-onboarding-001",)


@pytest.mark.asyncio
async def test_missing_supplier_does_not_call_servicenow() -> None:
    uow = InMemorySupplierUnitOfWork()
    servicenow_gateway = FakeServiceNowGateway()

    handler = RequestSupplierReviewHandler(
        unit_of_work=uow,
        servicenow_gateway=servicenow_gateway,
    )

    supplier_id = uuid4()

    with pytest.raises(SupplierNotFoundForReviewError):
        await handler.handle(
            RequestSupplierReviewCommand(
                supplier_id=supplier_id,
                risk_level="high",
                reason="Human review required.",
                policy_ids=("supplier-onboarding-001",),
            )
        )

    assert servicenow_gateway.created_requests == []
    assert servicenow_gateway.tickets == {}
