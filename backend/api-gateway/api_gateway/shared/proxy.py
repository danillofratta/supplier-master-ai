import httpx
from fastapi import HTTPException
from fastapi.responses import Response


HOP_BY_HOP_HEADERS = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding",
    "upgrade",
}


def to_gateway_response(
    upstream: httpx.Response,
) -> Response:
    headers = {
        key: value
        for key, value
        in upstream.headers.items()
        if key.lower()
        not in HOP_BY_HOP_HEADERS
        and key.lower()
        not in {
            "content-length",
            "content-encoding",
        }
    }

    return Response(
        content=upstream.content,
        status_code=upstream.status_code,
        headers=headers,
        media_type=upstream.headers.get(
            "content-type"
        ),
    )


def raise_gateway_error(
    exc: Exception,
) -> None:
    if isinstance(
        exc,
        httpx.TimeoutException,
    ):
        raise HTTPException(
            status_code=504,
            detail=(
                "Supplier service timed out."
            ),
        ) from exc

    if isinstance(
        exc,
        httpx.RequestError,
    ):
        raise HTTPException(
            status_code=503,
            detail=(
                "Supplier service unavailable."
            ),
        ) from exc

    raise exc
