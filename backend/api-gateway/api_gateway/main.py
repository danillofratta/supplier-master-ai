from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import (
    CORSMiddleware,
)

from api_gateway.bootstrap.settings import (
    get_settings,
)
from api_gateway.infrastructure.http.supplier_api_client import (
    SupplierApiClient,
)
from api_gateway.middleware.correlation_id import (
    CorrelationIdMiddleware,
)
from api_gateway.middleware.request_logging import RequestLoggingMiddleware
from api_gateway.routes.health import (
    router as health_router,
)
from api_gateway.routes.suppliers import (
    router as suppliers_router,
)

from api_gateway.shared.logging import (
    configure_logging,
)
from api_gateway.shared.observability import (
    configure_tracing,
    instrument_fastapi,
    instrument_httpx,
)


load_dotenv()

logger = configure_logging("api-gateway")
tracer = configure_tracing("api-gateway")
instrument_httpx()


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()

    app.state.supplier_api_client = (
        SupplierApiClient(
            base_url=(
                settings.supplier_api_url
            ),
            timeout_seconds=(
                settings
                .supplier_api_timeout_seconds
            ),
        )
    )

    try:
        yield
    finally:
        await (
            app.state.supplier_api_client
            .close()
        )


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="Supplier Master API Gateway",
        description=(
            "Edge API for Supplier Master services"
        ),
        version="1.0.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(
            settings.cors_origins
        ),
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=[
            "X-Correlation-ID",
        ],
    )

    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(
        CorrelationIdMiddleware
    )

    instrument_fastapi(app)

    app.include_router(health_router)
    app.include_router(suppliers_router)

    return app


app = create_app()
