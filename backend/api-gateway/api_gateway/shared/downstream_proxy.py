import logging
from time import perf_counter

import httpx
from fastapi import Request

from api_gateway.infrastructure.http.supplier_api_client import (
    SupplierApiClient,
)
from api_gateway.shared.proxy import (
    raise_gateway_error,
    to_gateway_response,
)


logger = logging.getLogger(__name__)


def _client(
    request: Request,
) -> SupplierApiClient:
    return request.app.state.supplier_api_client


def _correlation_id(
    request: Request,
) -> str:
    return request.state.correlation_id


async def proxy_supplier_request(
    request: Request,
    *,
    method: str,
    upstream_path: str,
):
    started = perf_counter()

    body = (
        await request.body()
        if method in {
            "POST",
            "PUT",
            "PATCH",
        }
        else None
    )

    logger.info(
        "downstream request started",
        extra={
            "component": "SupplierApiClient",
            "http_method": method,
            "downstream_path": upstream_path,
        },
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
            additional_headers={
                "Idempotency-Key": request.headers["idempotency-key"]
            }
            if "idempotency-key" in request.headers
            else None,
        )
    except (
        httpx.TimeoutException,
        httpx.RequestError,
    ) as exc:
        logger.exception(
            "downstream request failed",
            extra={
                "component": (
                    "SupplierApiClient"
                ),
                "http_method": method,
                "downstream_path": (
                    upstream_path
                ),
                "duration_ms": round(
                    (
                        perf_counter()
                        - started
                    )
                    * 1000,
                    2,
                ),
            },
        )
        raise_gateway_error(exc)

    logger.info(
        "downstream request completed",
        extra={
            "component": "SupplierApiClient",
            "http_method": method,
            "downstream_path": upstream_path,
            "downstream_status_code": (
                upstream.status_code
            ),
            "duration_ms": round(
                (
                    perf_counter()
                    - started
                )
                * 1000,
                2,
            ),
        },
    )

    return to_gateway_response(upstream)
