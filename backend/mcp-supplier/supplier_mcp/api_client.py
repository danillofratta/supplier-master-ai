from collections.abc import Mapping
from uuid import UUID, uuid4

import httpx

from supplier_mcp.exceptions import (
    ApiNotFoundError,
    OnboardingNotFoundError,
    SupplierApiError,
    SupplierNotFoundError,
)
from supplier_mcp.models import (
    OnboardingStatusResponse,
    StartOnboardingResponse,
    SupplierAnalysisResponse,
    SupplierListResponse,
    SupplierResponse,
)


class SupplierApiClient:
    def __init__(
        self,
        base_url: str,
    ) -> None:
        self._base_url = base_url.rstrip("/")

    async def health(self) -> str:
        return "Supplier Master MCP Server is healthy."

    async def _request(
        self,
        method: str,
        path: str,
        headers: Mapping[str, str] | None = None,
    ) -> dict | list:
        correlation_id = str(uuid4())
        url = f"{self._base_url}{path}"

        request_headers = dict(headers or {})
        # Correlation is generated per MCP -> Gateway request and cannot be
        # overridden by callers accidentally.
        request_headers["X-Correlation-ID"] = correlation_id

        try:
            timeout = httpx.Timeout(
                60.0,
                connect=10.0,
            )

            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=request_headers,
                )
        except httpx.RequestError as exc:
            raise SupplierApiError(
                f"An error occurred while requesting {exc.request.url}. "
                f"Error type: {type(exc).__name__}. "
                f"Details: {str(exc)}. "
                f"Correlation ID: {correlation_id}"
            ) from exc

        if response.status_code == 404:
            raise ApiNotFoundError(
                f"Resource not found at {path}. "
                f"Correlation ID: {correlation_id}"
            )

        if response.status_code >= 400:
            details = response.text.strip()
            raise SupplierApiError(
                f"Supplier API returned HTTP {response.status_code}. "
                f"Details: {details}. "
                f"Correlation ID: {correlation_id}"
            )

        return response.json()

    async def get_supplier(
        self,
        supplier_id: str,
    ) -> SupplierResponse:
        try:
            result = await self._request(
                method="GET",
                path=f"/api/v1/suppliers/{supplier_id}",
            )
        except ApiNotFoundError as exc:
            raise SupplierNotFoundError(
                f"Supplier {supplier_id} was not found."
            ) from exc

        return SupplierResponse.model_validate(result)

    async def get_suppliers(
        self,
    ) -> SupplierListResponse:
        result = await self._request(
            method="GET",
            path="/api/v1/suppliers",
        )
        return SupplierListResponse.model_validate(result)

    async def analyze_supplier(
        self,
        supplier_id: str,
    ) -> SupplierAnalysisResponse:
        try:
            result = await self._request(
                method="POST",
                path=f"/api/v1/suppliers/{supplier_id}/analysis",
            )
        except ApiNotFoundError as exc:
            raise SupplierNotFoundError(
                f"Supplier {supplier_id} was not found."
            ) from exc

        return SupplierAnalysisResponse.model_validate(result)

    async def get_onboarding_status(
        self,
        supplier_id: str,
    ) -> OnboardingStatusResponse:
        try:
            result = await self._request(
                method="GET",
                path=f"/api/v1/suppliers/{supplier_id}/onboarding",
            )
        except ApiNotFoundError as exc:
            raise OnboardingNotFoundError(
                f"No onboarding workflow was found "
                f"for supplier {supplier_id}."
            ) from exc

        return OnboardingStatusResponse.model_validate(result)

    async def start_onboarding(
        self,
        supplier_id: str,
        idempotency_key: UUID,
    ) -> StartOnboardingResponse:
        result = await self._request(
            method="POST",
            path=f"/api/v1/suppliers/{supplier_id}/onboarding",
            headers={
                "Idempotency-Key": str(idempotency_key),
            },
        )

        return StartOnboardingResponse.model_validate(result)
