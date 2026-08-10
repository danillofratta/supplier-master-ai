from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from backend.app.bootstrap.settings import Settings, get_settings
from backend.app.features.suppliers.analyze.exceptions import (
    SupplierAnalysisProviderError,
)
from backend.app.features.suppliers.analyze.handler import AnalyzeSupplierHandler
from backend.app.features.suppliers.analyze.policy_retriever import PolicyRetriever
from backend.app.features.suppliers.analyze.supplier_analyzer import SupplierAnalyzer
from backend.app.features.suppliers.create.handler import CreateSupplierHandler
from backend.app.infrastructure.persistence.sqlalchemy.database import Database
from backend.app.infrastructure.persistence.sqlalchemy.unit_of_work import (
    SqlAlchemySupplierUnitOfWork,
)
from backend.app.infrastructure.retrieval.null_policy_retriever import (
    NullPolicyRetriever,
)
from backend.app.shared.unit_of_work import SupplierUnitOfWork


@lru_cache
def _build_database(database_url: str) -> Database:
    return Database(database_url)


def get_database(
    settings: Annotated[Settings, Depends(get_settings)],
) -> Database:
    return _build_database(settings.database_url)


def get_supplier_unit_of_work(
    database: Annotated[Database, Depends(get_database)],
) -> SupplierUnitOfWork:
    return SqlAlchemySupplierUnitOfWork(database.session_factory)


SupplierUnitOfWorkDependency = Annotated[
    SupplierUnitOfWork,
    Depends(get_supplier_unit_of_work),
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


@lru_cache
def _build_policy_retriever() -> PolicyRetriever:
    return NullPolicyRetriever()


def get_policy_retriever() -> PolicyRetriever:
    return _build_policy_retriever()


def get_analyze_supplier_handler(
    unit_of_work: SupplierUnitOfWorkDependency,
    analyzer: Annotated[SupplierAnalyzer, Depends(get_supplier_analyzer)],
    policy_retriever: Annotated[PolicyRetriever, Depends(get_policy_retriever)],
) -> AnalyzeSupplierHandler:
    return AnalyzeSupplierHandler(
        unit_of_work=unit_of_work,
        supplier_analyzer=analyzer,
        policy_retriever=policy_retriever,
    )


def get_create_supplier_handler(
    unit_of_work: SupplierUnitOfWorkDependency,
) -> CreateSupplierHandler:
    return CreateSupplierHandler(unit_of_work)
