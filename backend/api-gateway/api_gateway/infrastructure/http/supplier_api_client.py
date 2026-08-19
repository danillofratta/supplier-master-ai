from collections.abc import Mapping

import httpx


class SupplierApiClient:
    def __init__(
        self,
        *,
        base_url: str,
        timeout_seconds: float,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._owns_client = client is None
        self._client = client or httpx.AsyncClient(
            timeout=httpx.Timeout(
                timeout_seconds
            ),
            follow_redirects=True,
        )

    async def close(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    async def request(
        self,
        *,
        method: str,
        path: str,
        correlation_id: str,
        params: Mapping[str, str] | None = None,
        content: bytes | None = None,
        content_type: str | None = None,
        authorization: str | None = None,
    ) -> httpx.Response:
        headers = {
            "X-Correlation-ID": correlation_id,
            "Accept": "application/json",
        }

        if content_type:
            headers["Content-Type"] = content_type

        if authorization:
            headers["Authorization"] = authorization

        return await self._client.request(
            method=method,
            url=f"{self._base_url}{path}",
            params=params,
            content=content,
            headers=headers,
        )

    async def health(
        self,
        *,
        correlation_id: str,
    ) -> httpx.Response:
        return await self.request(
            method="GET",
            path="/health",
            correlation_id=correlation_id,
        )
