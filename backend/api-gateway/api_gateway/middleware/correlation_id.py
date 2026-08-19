from uuid import UUID, uuid4

from starlette.middleware.base import (
    BaseHTTPMiddleware,
)
from starlette.requests import Request


CORRELATION_ID_HEADER = "X-Correlation-ID"


def resolve_correlation_id(
    value: str | None,
) -> str:
    if value:
        try:
            return str(UUID(value))
        except ValueError:
            pass

    return str(uuid4())


class CorrelationIdMiddleware(
    BaseHTTPMiddleware
):
    async def dispatch(
        self,
        request: Request,
        call_next,
    ):
        correlation_id = resolve_correlation_id(
            request.headers.get(
                CORRELATION_ID_HEADER
            )
        )

        request.state.correlation_id = (
            correlation_id
        )

        response = await call_next(request)
        response.headers[
            CORRELATION_ID_HEADER
        ] = correlation_id

        return response
