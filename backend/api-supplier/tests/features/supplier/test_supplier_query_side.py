from uuid import uuid4

import pytest

from api_supplier.domain.entities.address import Address
from api_supplier.domain.entities.supplier import Supplier
from api_supplier.domain.entities.supplier_onboarding_workflow import (
    SupplierOnboardingWorkflow,
)
from api_supplier.features.suppliers.get_by_id.handler import (
    GetSupplierByIdHandler,
)
from api_supplier.features.suppliers.get_by_id.query import (
    GetSupplierByIdQuery,
)
from api_supplier.features.suppliers.get_list.handler import (
    ListSuppliersHandler,
)
from api_supplier.features.suppliers.get_list.query import (
    ListSuppliersQuery,
)
from api_supplier.features.suppliers.get_onboarding_status.handler import (
    GetSupplierOnboardingHandler,
)
from api_supplier.features.suppliers.get_onboarding_status.query import (
    GetSupplierOnboardingQuery,
)
from api_supplier.infrastructure.persistence.in_memory_unit_of_work import (
    InMemorySupplierUnitOfWork,
)


def make_supplier(name: str = "ACME") -> Supplier:
    return Supplier(
        supplier_id=uuid4(),
        name=name,
        email="contact@acme.test",
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
async def test_list_suppliers_returns_items() -> None:
    uow = InMemorySupplierUnitOfWork()
    supplier = make_supplier()
    await uow.suppliers.add(supplier)

    result = await ListSuppliersHandler(uow).handle(
        ListSuppliersQuery()
    )

    assert len(result.items) == 1
    assert result.items[0].supplier_id == supplier.supplier_id
    assert result.items[0].name == "ACME"


@pytest.mark.asyncio
async def test_get_supplier_by_id_returns_supplier() -> None:
    uow = InMemorySupplierUnitOfWork()
    supplier = make_supplier()
    await uow.suppliers.add(supplier)

    result = await GetSupplierByIdHandler(uow).handle(
        GetSupplierByIdQuery(
            supplier_id=supplier.supplier_id
        )
    )

    assert result is not None
    assert result.supplier_id == supplier.supplier_id
    assert result.city == "Sao Paulo"


@pytest.mark.asyncio
async def test_get_latest_onboarding_for_supplier() -> None:
    uow = InMemorySupplierUnitOfWork()
    supplier = make_supplier()
    await uow.suppliers.add(supplier)

    workflow = SupplierOnboardingWorkflow.start(
        supplier_id=supplier.supplier_id
    )
    await uow.onboarding_workflows.add(workflow)

    result = await GetSupplierOnboardingHandler(
        uow
    ).handle(
        GetSupplierOnboardingQuery(
            supplier_id=supplier.supplier_id
        )
    )

    assert result is not None
    assert result.workflow_id == workflow.workflow_id
    assert result.correlation_id == workflow.correlation_id
