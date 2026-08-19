from fastapi import FastAPI

from api_supplier.shared.observability import configure_tracing

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


tracer = configure_tracing("api-supplier")


def create_app() -> FastAPI:
    app = FastAPI(
        title="Supplier Management API",
        description="API for managing and analyzing suppliers",
        version="1.0.0",
    )

    try:
        from opentelemetry.instrumentation.fastapi import (
            FastAPIInstrumentor,
        )
        FastAPIInstrumentor.instrument_app(app)
    except ImportError:
        pass

    register_exception_handlers(app)
    app.include_router(create_supplier_router)
    app.include_router(analyze_supplier_router)
    app.include_router(list_suppliers_router)
    app.include_router(get_supplier_by_id_router)
    app.include_router(get_supplier_onboarding_router)

    @app.get("/health", tags=["Health"])
    async def health_check() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
