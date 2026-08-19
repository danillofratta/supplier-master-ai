from uuid import UUID

import httpx
from fastapi import (
    APIRouter,
    Request,
)

from api_gateway.infrastructure.http.supplier_api_client import (
    SupplierApiClient,
)
from api_gateway.shared.proxy import (
    raise_gateway_error,
    to_gateway_response,
)


router = APIRouter(
    prefix="/api/v1/suppliers",
    tags=["Suppliers"],
)


def _client(
    request: Request,
) -> SupplierApiClient:
    return request.app.state.supplier_api_client


def _correlation_id(
    request: Request,
) -> str:
    return request.state.correlation_id


async def _proxy(
    request: Request,
    *,
    method: str,
    upstream_path: str,
):
    body = (
        await request.body()
        if method in {"POST", "PUT", "PATCH"}
        else None
    )

    try:
        upstream = await _client(
            request
        ).request(
            method=method,
            path=upstream_path,
            correlation_id=_correlation_id(
                request
            ),
            params=dict(
                request.query_params
            ),
            content=body,
            content_type=request.headers.get(
                "content-type"
            ),
            authorization=request.headers.get(
                "authorization"
            ),
        )
    except (
        httpx.TimeoutException,
        httpx.RequestError,
    ) as exc:
        raise_gateway_error(exc)

    return to_gateway_response(upstream)


@router.get("")
async def list_suppliers(
    request: Request,
):
    return await _proxy(
        request,
        method="GET",
        upstream_path="/v1/suppliers",
    )


@router.post("")
async def create_supplier(
    request: Request,
):
    return await _proxy(
        request,
        method="POST",
        upstream_path="/v1/suppliers/",
    )


@router.get("/{supplier_id}")
async def get_supplier(
    supplier_id: UUID,
    request: Request,
):
    return await _proxy(
        request,
        method="GET",
        upstream_path=(
            f"/v1/suppliers/{supplier_id}"
        ),
    )


@router.post(
    "/{supplier_id}/analysis"
)
async def analyze_supplier(
    supplier_id: UUID,
    request: Request,
):
    return await _proxy(
        request,
        method="POST",
        upstream_path=(
            f"/v1/suppliers/"
            f"{supplier_id}/analysis"
        ),
    )


@router.get(
    "/{supplier_id}/onboarding"
)
async def get_supplier_onboarding(
    supplier_id: UUID,
    request: Request,
):
    return await _proxy(
        request,
        method="GET",
        upstream_path=(
            f"/v1/suppliers/"
            f"{supplier_id}/onboarding"
        ),
    )
