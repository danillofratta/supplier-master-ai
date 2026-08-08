from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from backend.app.features.suppliers.analyze.exceptions import SupplierAnalysisProviderError
from backend.app.features.suppliers.analyze.supplier_analyzer import SupplierAnalyzer
from backend.app.bootstrap.settings import Settings, get_settings
from backend.app.domain.repositories.supplier_repository import SupplierRepository
from backend.app.features.suppliers.analyze.handler import AnalyzeSupplierHandler
from backend.app.features.suppliers.create.handler import CreateSupplierHandler
from backend.app.infrastructure.repositories.supplier_repository import (
    InMemorySupplierRepository,
)

_repository_instance = InMemorySupplierRepository()


def get_supplier_repository() -> SupplierRepository:
    return _repository_instance


SupplierRepositoryDependency = Annotated[
    SupplierRepository,
    Depends(get_supplier_repository),
]


@lru_cache
def _build_supplier_analyzer(
    region_name: str,
    model_id: str,
    temperature: float,
    max_tokens: int,
) -> SupplierAnalyzer:
    try:
        from backend.app.infrastructure.ai.bedrock_supplier_analyzer import (
            BedrockSupplierAnalyzer,
        )
    except ModuleNotFoundError as exc:
        if exc.name in {"boto3", "botocore"}:
            raise SupplierAnalysisProviderError(
                "Amazon Bedrock support is not installed. Install the 'ai' extra."
            ) from exc
        raise

    return BedrockSupplierAnalyzer(
        region_name=region_name,
        model_id=model_id,
        temperature=temperature,
        max_tokens=max_tokens,
    )


def get_supplier_analyzer(
    settings: Annotated[Settings, Depends(get_settings)],
) -> SupplierAnalyzer:
    if not settings.bedrock_model_id:
        raise SupplierAnalysisProviderError(
            "BEDROCK_MODEL_ID is required to analyze suppliers."
        )

    return _build_supplier_analyzer(
        settings.aws_region,
        settings.bedrock_model_id,
        settings.bedrock_temperature,
        settings.bedrock_max_tokens,
    )


def get_analyze_supplier_handler(
    repository: SupplierRepositoryDependency,
    analyzer: Annotated[SupplierAnalyzer, Depends(get_supplier_analyzer)],
) -> AnalyzeSupplierHandler:
    return AnalyzeSupplierHandler(repository, analyzer)


def get_create_supplier_handler(
    repository: SupplierRepositoryDependency,
) -> CreateSupplierHandler:
    return CreateSupplierHandler(repository)
