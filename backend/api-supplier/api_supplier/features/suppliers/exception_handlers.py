import logging

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from api_supplier.domain.exceptions import DomainError
from api_supplier.features.suppliers.analyze.exceptions import SupplierNotFoundError
from api_supplier.features.suppliers.create.exceptions import (
    SupplierAlreadyExistsError,
)
from api_supplier.features.suppliers.analyze.exceptions import (
    InvalidSupplierAnalysisResponseError,
    SupplierAnalysisProviderError,
)

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(SupplierAlreadyExistsError)
    async def handle_supplier_already_exists(
        request: Request,
        exc: SupplierAlreadyExistsError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "code": "supplier_already_exists",
                "message": "A supplier with this tax ID already exists.",
                "details": {"tax_id": exc.tax_id},
            },
        )

    @app.exception_handler(SupplierNotFoundError)
    async def handle_supplier_not_found(
        request: Request,
        exc: SupplierNotFoundError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "code": "supplier_not_found",
                "message": "The supplier was not found.",
                "details": {"supplier_id": str(exc.supplier_id)},
            },
        )

    @app.exception_handler(InvalidSupplierAnalysisResponseError)
    async def handle_invalid_analysis_response(
        request: Request,
        exc: InvalidSupplierAnalysisResponseError,
    ) -> JSONResponse:
        logger.exception(
            "AI provider returned an invalid response",
            exc_info=(type(exc), exc, exc.__traceback__),
            extra={
                "component": "SupplierAnalysis",
                "http_path": request.url.path,
            },
        )
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content={
                "code": "invalid_ai_provider_response",
                "message": "The AI provider returned an invalid response.",
            },
        )

    @app.exception_handler(SupplierAnalysisProviderError)
    async def handle_analysis_provider_error(
        request: Request,
        exc: SupplierAnalysisProviderError,
    ) -> JSONResponse:
        logger.exception(
            "AI analysis provider unavailable",
            exc_info=(type(exc), exc, exc.__traceback__),
            extra={
                "component": "SupplierAnalysis",
                "http_path": request.url.path,
            },
        )
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "code": "ai_provider_unavailable",
                "message": "The AI analysis provider is temporarily unavailable.",
            },
        )

    @app.exception_handler(DomainError)
    async def handle_domain_error(
        request: Request,
        exc: DomainError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "code": "domain_rule_violation",
                "message": str(exc),
            },
        )

    @app.exception_handler(RequestValidationError)
    async def handle_request_validation(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "code": "request_validation_error",
                "message": "The request contains invalid data.",
                "details": jsonable_encoder(exc.errors()),
            },
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        logger.exception(
            "Unexpected error while processing %s %s",
            request.method,
            request.url.path,
            exc_info=(type(exc), exc, exc.__traceback__),
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "code": "internal_server_error",
                "message": "An unexpected error occurred.",
            },
        )
