from fastapi import APIRouter, Request

from api_gateway.shared.downstream_proxy import (
    proxy_supplier_request,
)


router = APIRouter(
    prefix="/api/v1/policies",
    tags=["Policies"],
)


@router.post("/ingest")
async def ingest_policy(
    request: Request,
):
    return await proxy_supplier_request(
        request,
        method="POST",
        upstream_path="/v1/policies/ingest",
    )
