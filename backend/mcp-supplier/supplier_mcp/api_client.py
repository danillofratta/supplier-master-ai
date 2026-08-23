from asyncio import timeout

import httpx
from uuid import uuid4
from supplier_mcp.models import OnboardingStatusResponse, SupplierAnalysisResponse, SupplierResponse, SupplierListResponse
from supplier_mcp.exceptions import (
    SupplierApiError,
    ApiNotFoundError,
    SupplierNotFoundError,
    OnboardingNotFoundError
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
    ) -> dict | list:
        correlation_id = str(uuid4())

        url = f"{self._base_url}{path}"

        headers = {
            "X-Correlation-ID": correlation_id
        }

        try:
            timeout = httpx.Timeout(
                60.0,
                connect=10.0,
            )

            async with httpx.AsyncClient( timeout=timeout) as client:
                response = await client.request(method, url, headers=headers)
        except httpx.RequestError as exc:
            raise SupplierApiError(
                f"An error occurred while requesting {exc.request.url}. "
                f"Error type: {type(exc).__name__}. "
                f"Details: {str(exc)}. "
                f"Correlation ID: {correlation_id}"
    ) from exc                
        # except httpx.RequestError as exc:
        #     raise SupplierApiError(
        #         f"An error occurred while requesting {exc.request.url!r}. "
        #         f"Correlation ID: {correlation_id}"
        #     ) from exc

        if response.status_code == 404:
            raise ApiNotFoundError(
                f"Resource not found at {path}. "
                f"Correlation ID: {correlation_id}"
            )

        if response.status_code >= 400:
            raise SupplierApiError(
                f"Supplier API returned HTTP "
                f"{response.status_code}. "
                f"Correlation ID: {correlation_id}"
            )

        return response.json()        

    async def get_supplier(
        self,
        supplier_id: str,
    ) -> SupplierResponse:
        result = await self._request(
            method="GET",
            path=f"/api/v1/suppliers/{supplier_id}",
        )

        return SupplierResponse.model_validate(result)

    async def get_suppliers(
        self,
    ) -> SupplierListResponse:

        try:
            result = await self._request(
                method="GET",
                path="/api/v1/suppliers",
            )

        except ApiNotFoundError as exc:
            raise SupplierNotFoundError(
                f"Suppliers were not found."
            ) from exc

        return SupplierListResponse.model_validate(
            result
        )

    async def analyze_supplier(
        self,
        supplier_id: str,
    ) -> SupplierAnalysisResponse:
        result = await self._request(
            method="POST",
            path=f"/api/v1/suppliers/{supplier_id}/analysis",
        )

        return SupplierAnalysisResponse.model_validate(
            result
        )

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