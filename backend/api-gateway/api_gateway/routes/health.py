import httpx
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from api_gateway.infrastructure.http.supplier_api_client import (
    SupplierApiClient,
)


router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


@router.get("")
async def health():
    return {
        "status": "ok",
        "service": "api-gateway",
    }


@router.get("/live")
async def liveness():
    return {
        "status": "ok",
        "service": "api-gateway",
    }


@router.get("/ready")
async def readiness(
    request: Request,
):
    client: SupplierApiClient = (
        request.app.state.supplier_api_client
    )

    try:
        response = await client.health(
            correlation_id=(
                request.state.correlation_id
            )
        )
        supplier_ready = (
            200 <= response.status_code < 300
        )
    except (
        httpx.TimeoutException,
        httpx.RequestError,
    ):
        supplier_ready = False

    status_code = (
        200
        if supplier_ready
        else 503
    )

    return JSONResponse(
        status_code=status_code,
        content={
            "status": (
                "ready"
                if supplier_ready
                else "not_ready"
            ),
            "services": {
                "api-gateway": "up",
                "api-supplier": (
                    "up"
                    if supplier_ready
                    else "down"
                ),
            },
        },
    )
