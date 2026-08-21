from uuid import UUID

from fastapi import APIRouter, Request

from api_gateway.shared.downstream_proxy import (
    proxy_supplier_request,
)


router = APIRouter(
    prefix="/api/v1/suppliers",
    tags=["Suppliers"],
)


@router.get("")
async def list_suppliers(
    request: Request,
):
    return await proxy_supplier_request(
        request,
        method="GET",
        upstream_path="/v1/suppliers",
    )


@router.post("")
async def create_supplier(
    request: Request,
):
    return await proxy_supplier_request(
        request,
        method="POST",
        upstream_path="/v1/suppliers/",
    )


@router.get("/{supplier_id}")
async def get_supplier(
    supplier_id: UUID,
    request: Request,
):
    return await proxy_supplier_request(
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
    return await proxy_supplier_request(
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
    return await proxy_supplier_request(
        request,
        method="GET",
        upstream_path=(
            f"/v1/suppliers/"
            f"{supplier_id}/onboarding"
        ),
    )


@router.post(
    "/{supplier_id}/onboarding"
)
async def start_supplier_onboarding(
    supplier_id: UUID,
    request: Request,
):
    return await proxy_supplier_request(
        request,
        method="POST",
        upstream_path=(
            f"/v1/suppliers/"
            f"{supplier_id}/onboarding"
        ),
    )


@router.post(
    "/{supplier_id}/onboarding/review-decision"
)
async def decide_supplier_review(
    supplier_id: UUID,
    request: Request,
):
    return await proxy_supplier_request(
        request,
        method="POST",
        upstream_path=(
            f"/v1/suppliers/"
            f"{supplier_id}/onboarding/review-decision"
        ),
    )
