from fastapi import FastAPI

from api_supplier.features.suppliers.analyze.endpoint import (
    router as analyze_supplier_router,
)
from api_supplier.features.suppliers.create.endpoint import (
    router as create_supplier_router,
)
from api_supplier.features.suppliers.exception_handlers import (
    register_exception_handlers,
)


def create_app() -> FastAPI:
    app = FastAPI(
        title="Supplier Management API",
        description="API for managing and analyzing suppliers",
        version="1.0.0",
    )

    register_exception_handlers(app)
    app.include_router(create_supplier_router)
    app.include_router(analyze_supplier_router)

    @app.get("/health", tags=["Health"])
    async def health_check() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
