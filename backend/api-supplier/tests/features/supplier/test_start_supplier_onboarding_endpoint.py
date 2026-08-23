from types import SimpleNamespace
from uuid import UUID, uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient

from api_supplier.bootstrap.dependencies import (
    get_start_supplier_onboarding_handler,
)
from api_supplier.domain.enums.supplier_onboarding_status import (
    SupplierOnboardingStatus,
)
from api_supplier.features.suppliers.onboarding_workflow.endpoint import router


class FakeStartSupplierOnboardingHandler:
    def __init__(self) -> None:
        self.command = None

    async def handle(self, command):
        self.command = command
        return SimpleNamespace(
            onboarding_workflow_id=uuid4(),
            supplier_id=command.supplier_id,
            status=SupplierOnboardingStatus.PENDING,
        )


def build_client(handler: FakeStartSupplierOnboardingHandler) -> TestClient:
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[
        get_start_supplier_onboarding_handler
    ] = lambda: handler
    return TestClient(app)


def test_start_onboarding_requires_idempotency_key_header() -> None:
    handler = FakeStartSupplierOnboardingHandler()
    supplier_id = uuid4()

    with build_client(handler) as client:
        response = client.post(
            f"/v1/suppliers/{supplier_id}/onboarding"
        )

    assert response.status_code == 422
    assert handler.command is None


def test_start_onboarding_passes_idempotency_key_to_command() -> None:
    handler = FakeStartSupplierOnboardingHandler()
    supplier_id = uuid4()
    idempotency_key = uuid4()

    with build_client(handler) as client:
        response = client.post(
            f"/v1/suppliers/{supplier_id}/onboarding",
            headers={"Idempotency-Key": str(idempotency_key)},
        )

    assert response.status_code == 201
    assert handler.command is not None
    assert handler.command.supplier_id == supplier_id
    assert handler.command.idempotency_key == idempotency_key
    assert isinstance(handler.command.idempotency_key, UUID)
