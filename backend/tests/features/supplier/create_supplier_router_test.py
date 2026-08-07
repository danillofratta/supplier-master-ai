from uuid import UUID, uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.app.dependencies import get_create_supplier_handler
from backend.app.domain.entities.address import Address
from backend.app.domain.entities.supplier import Supplier
from backend.app.domain.enums.supplier_status import SupplierStatus
from backend.app.features.suppliers.create.endpoint import router
from backend.app.features.suppliers.create.exceptions import SupplierAlreadyExistsError
from backend.app.features.suppliers.exception_handlers import register_exception_handlers


class FakeCreateSupplierHandler:
    def __init__(self, supplier: Supplier) -> None:
        self.supplier = supplier
        self.received_command = None

    async def handle(self, command):
        self.received_command = command
        return self.supplier


class DuplicateSupplierHandler:
    def __init__(self) -> None:
        self.calls = 0

    async def handle(self, command):
        self.calls += 1

        if self.calls == 1:
            return build_supplier(uuid4())

        raise SupplierAlreadyExistsError(command.tax_id)


def create_test_app(handler) -> FastAPI:
    app = FastAPI()

    register_exception_handlers(app)
    app.include_router(router)

    app.dependency_overrides[
        get_create_supplier_handler
    ] = lambda: handler

    return app


def build_supplier(supplier_id: UUID) -> Supplier:
    return Supplier(
        supplier_id=supplier_id,
        name="ACME Supplies",
        email="contato@acme.com",
        phone="11999999999",
        tax_id="12345678000199",
        status=SupplierStatus.DRAFT,
        address=Address(
            street="Rua A",
            city="Sao Paulo",
            state="SP",
            zip_code="01000-000",
            country="Brasil",
        ),
    )

def test_create_supplier_returns_created_supplier() -> None:
    supplier_id = uuid4()
    fake_handler = FakeCreateSupplierHandler(
        build_supplier(supplier_id)
    )
    app = create_test_app(fake_handler)

    with TestClient(app) as client:
        response = client.post(
            "/v1/suppliers/",
            json={
                "name": "ACME Supplies",
                "email": "contato@acme.com",
                "phone": "11999999999",
                "tax_id": "12345678000199",
                "address": {
                    "street": "Rua A",
                    "city": "Sao Paulo",
                    "state": "SP",
                    "zip_code": "01000-000",
                    "country": "Brasil",
                },
            },
        )

    assert response.status_code == 201

    body = response.json()

    assert body["supplier_id"] == str(supplier_id)
    assert body["name"] == "ACME Supplies"
    assert body["tax_id"] == "12345678000199"

    assert fake_handler.received_command is not None
    assert fake_handler.received_command.name == "ACME Supplies"
    assert fake_handler.received_command.address.city == "Sao Paulo"

def test_duplicate_supplier_returns_conflict() -> None:
    payload = {
        "name": "ACME Supplies",
        "email": "contato@acme.com",
        "phone": "11999999999",
        "tax_id": "12.345.678/0001-99",
        "address": {
            "street": "Rua A",
            "city": "Sao Paulo",
            "state": "SP",
            "zip_code": "01000-000",
            "country": "Brasil",
        },
    }
    app = create_test_app(DuplicateSupplierHandler())

    with TestClient(app) as client:
        first_response = client.post("/v1/suppliers/", json=payload)
        second_response = client.post("/v1/suppliers/", json=payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json() == {
        "code": "supplier_already_exists",
        "message": "A supplier with this tax ID already exists.",
        "details": {"tax_id": payload["tax_id"]},
    }
