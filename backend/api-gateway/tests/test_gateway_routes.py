import httpx
from fastapi.testclient import TestClient

from api_gateway.main import create_app


class FakeSupplierApiClient:
    def __init__(self) -> None:
        self.calls: list[dict] = []
        self.health_status = 200
        self.raise_error: Exception | None = None

    async def close(self) -> None:
        return None

    async def request(
        self,
        *,
        method,
        path,
        correlation_id,
        params=None,
        content=None,
        content_type=None,
        authorization=None,
    ) -> httpx.Response:
        if self.raise_error is not None:
            raise self.raise_error

        self.calls.append({
            "method": method,
            "path": path,
            "correlation_id": correlation_id,
            "params": params,
            "content": content,
            "content_type": content_type,
            "authorization": authorization,
        })

        return httpx.Response(
            status_code=200,
            json={
                "path": path,
                "method": method,
            },
            request=httpx.Request(
                method,
                f"http://supplier{path}",
            ),
        )

    async def health(
        self,
        *,
        correlation_id,
    ) -> httpx.Response:
        return httpx.Response(
            status_code=self.health_status,
            json={"status": "ok"},
            request=httpx.Request(
                "GET",
                "http://supplier/health",
            ),
        )


def test_list_suppliers_is_proxied_and_correlation_id_is_propagated() -> None:
    app = create_app()

    with TestClient(app) as client:
        fake = FakeSupplierApiClient()
        app.state.supplier_api_client = fake

        correlation_id = (
            "11111111-1111-1111-1111-111111111111"
        )

        response = client.get(
            "/api/v1/suppliers",
            headers={
                "X-Correlation-ID": correlation_id
            },
        )

        assert response.status_code == 200
        assert response.headers[
            "X-Correlation-ID"
        ] == correlation_id
        assert fake.calls[0]["path"] == "/v1/suppliers"
        assert (
            fake.calls[0]["correlation_id"]
            == correlation_id
        )


def test_create_supplier_is_proxied() -> None:
    app = create_app()

    with TestClient(app) as client:
        fake = FakeSupplierApiClient()
        app.state.supplier_api_client = fake

        response = client.post(
            "/api/v1/suppliers",
            json={"name": "ACME"},
        )

        assert response.status_code == 200
        assert fake.calls[0]["method"] == "POST"
        assert fake.calls[0]["path"] == "/v1/suppliers/"
        assert fake.calls[0]["content"]


def test_supplier_timeout_returns_504() -> None:
    app = create_app()

    with TestClient(app) as client:
        fake = FakeSupplierApiClient()
        fake.raise_error = httpx.ReadTimeout(
            "timeout"
        )
        app.state.supplier_api_client = fake

        response = client.get(
            "/api/v1/suppliers"
        )

        assert response.status_code == 504
        assert response.json()["detail"] == (
            "Supplier service timed out."
        )


def test_readiness_returns_503_when_supplier_is_down() -> None:
    app = create_app()

    with TestClient(app) as client:
        fake = FakeSupplierApiClient()
        fake.health_status = 503
        app.state.supplier_api_client = fake

        response = client.get(
            "/health/ready"
        )

        assert response.status_code == 503
        assert response.json()["services"][
            "api-supplier"
        ] == "down"


def test_detail_analysis_and_onboarding_routes_are_proxied() -> None:
    app = create_app()

    with TestClient(app) as client:
        fake = FakeSupplierApiClient()
        app.state.supplier_api_client = fake
        supplier_id = "11111111-1111-1111-1111-111111111111"

        detail = client.get(
            f"/api/v1/suppliers/{supplier_id}"
        )
        analysis = client.post(
            f"/api/v1/suppliers/{supplier_id}/analysis"
        )
        onboarding = client.get(
            f"/api/v1/suppliers/{supplier_id}/onboarding"
        )

        assert detail.status_code == 200
        assert analysis.status_code == 200
        assert onboarding.status_code == 200
        assert fake.calls[0]["path"] == f"/v1/suppliers/{supplier_id}"
        assert fake.calls[1]["path"] == f"/v1/suppliers/{supplier_id}/analysis"
        assert fake.calls[2]["path"] == f"/v1/suppliers/{supplier_id}/onboarding"


def test_authorization_header_is_forwarded() -> None:
    app = create_app()

    with TestClient(app) as client:
        fake = FakeSupplierApiClient()
        app.state.supplier_api_client = fake

        response = client.get(
            "/api/v1/suppliers",
            headers={"Authorization": "Bearer token"},
        )

        assert response.status_code == 200
        assert fake.calls[0]["authorization"] == "Bearer token"


def test_onboarding_command_routes_are_proxied() -> None:
    app = create_app()

    with TestClient(app) as client:
        fake = FakeSupplierApiClient()
        app.state.supplier_api_client = fake
        supplier_id = "11111111-1111-1111-1111-111111111111"

        start = client.post(
            f"/api/v1/suppliers/{supplier_id}/onboarding"
        )
        review = client.post(
            f"/api/v1/suppliers/{supplier_id}/onboarding/review-decision",
            json={"decision": "approve"},
        )

        assert start.status_code == 200
        assert review.status_code == 200
        assert fake.calls[0]["path"] == (
            f"/v1/suppliers/{supplier_id}/onboarding"
        )
        assert fake.calls[1]["path"] == (
            f"/v1/suppliers/{supplier_id}/onboarding/review-decision"
        )


def test_policy_ingest_is_proxied() -> None:
    app = create_app()

    with TestClient(app) as client:
        fake = FakeSupplierApiClient()
        app.state.supplier_api_client = fake

        response = client.post(
            "/api/v1/policies/ingest",
            json={"document_id": "policy-001"},
        )

        assert response.status_code == 200
        assert fake.calls[0]["method"] == "POST"
        assert fake.calls[0]["path"] == "/v1/policies/ingest"
        assert fake.calls[0]["content"]
