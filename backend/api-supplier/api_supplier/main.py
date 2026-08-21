from contextlib import asynccontextmanager

from fastapi import FastAPI

from api_supplier.shared.observability import (
    configure_tracing,
    instrument_botocore,
    instrument_fastapi,
)
from api_supplier.shared.logging import configure_logging
from api_supplier.middleware.correlation_id import CorrelationIdMiddleware
from api_supplier.middleware.request_logging import RequestLoggingMiddleware
from api_supplier.bootstrap.dependencies import dispose_database
from api_supplier.bootstrap.settings import get_settings

from api_supplier.features.suppliers.analyze.endpoint import (
    router as analyze_supplier_router,
)
from api_supplier.features.suppliers.create.endpoint import (
    router as create_supplier_router,
)

from api_supplier.features.suppliers.get_list.endpoint import (
    router as list_suppliers_router,
)
from api_supplier.features.suppliers.get_by_id.endpoint import (
    router as get_supplier_by_id_router,
)
from api_supplier.features.suppliers.get_onboarding_status.endpoint import (
    router as get_supplier_onboarding_router,
)
from api_supplier.features.suppliers.exception_handlers import (
    register_exception_handlers,
)
from api_supplier.features.suppliers.onboarding_workflow.endpoint import router as onboarding_workflow_router
from api_supplier.features.suppliers.review_decision.endpoint import router as review_decision_router
from api_supplier.features.policies.ingest.endpoint import router as ingest_policy_router


logger = configure_logging("api-supplier")
tracer = configure_tracing("api-supplier")
instrument_botocore()


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        yield
    finally:
        await dispose_database(
            get_settings()
        )


def create_app() -> FastAPI:
    app = FastAPI(
        title="Supplier Management API",
        description="API for managing and analyzing suppliers",
        version="1.0.0",
        lifespan=lifespan,
    )


    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(CorrelationIdMiddleware)
    instrument_fastapi(app)

    register_exception_handlers(app)
    app.include_router(create_supplier_router)
    app.include_router(analyze_supplier_router)
    app.include_router(list_suppliers_router)
    app.include_router(get_supplier_by_id_router)
    app.include_router(get_supplier_onboarding_router)
    app.include_router(onboarding_workflow_router)
    app.include_router(review_decision_router)
    app.include_router(ingest_policy_router)

    @app.get("/health", tags=["Health"])
    async def health_check() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
