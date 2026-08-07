from fastapi import FastAPI

from backend.app.features.suppliers.create.endpoint import router
from backend.app.features.suppliers.exception_handlers import register_exception_handlers


def create_app() -> FastAPI:
    app = FastAPI(
        title="Supplier Management API",
        description="API for managing suppliers",
        version="1.0.0",
    )

    register_exception_handlers(app)
    app.include_router(router)

    @app.get("/health", tags=["Health"])
    async def health_check() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()