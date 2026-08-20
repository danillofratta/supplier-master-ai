import logging
from time import perf_counter

from starlette.middleware.base import (
    BaseHTTPMiddleware,
)
from starlette.requests import Request


logger = logging.getLogger("http.request")


class RequestLoggingMiddleware(
    BaseHTTPMiddleware
):
    async def dispatch(
        self,
        request: Request,
        call_next,
    ):
        started = perf_counter()

        logger.info(
            "HTTP request started",
            extra={
                "http_method": request.method,
                "http_path": request.url.path,
            },
        )

        try:
            response = await call_next(request)
        except Exception:
            logger.exception(
                "HTTP request failed",
                extra={
                    "http_method": request.method,
                    "http_path": request.url.path,
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
            raise

        logger.info(
            "HTTP request completed",
            extra={
                "http_method": request.method,
                "http_path": request.url.path,
                "http_status_code": (
                    response.status_code
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

        return response
