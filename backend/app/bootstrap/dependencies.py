from functools import lru_cache
from typing import Annotated, Any

from fastapi import Depends

from backend.app.bootstrap.settings import Settings, get_settings
from backend.app.features.policies.ingest.embedding_provider import EmbeddingProvider
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
def _build_embedding_provider(
    region_name: str,
    model_id: str,
    dimensions: int,
) -> EmbeddingProvider:
    try:
        from backend.app.infrastructure.ai.bedrock.titan_embedding_provider import (
            TitanEmbeddingProvider,
        )
    except ModuleNotFoundError as exc:
        raise SupplierAnalysisProviderError(
            "Embedding support is not installed. Install the 'retrieval' extra."
        ) from exc

    return TitanEmbeddingProvider(
        region_name=region_name,
        model_id=model_id,
        dimensions=dimensions,
    )


def get_embedding_provider(
    settings: Annotated[Settings, Depends(get_settings)],
) -> EmbeddingProvider:
    return _build_embedding_provider(
        settings.aws_region,
        settings.embedding_model_id,
        settings.embedding_dimensions,
    )


@lru_cache
def _build_opensearch_client(
    endpoint: str,
    region: str,
    service: str,
) -> Any:
    try:
        from backend.app.infrastructure.retrieval.opensearch.client import (
            create_opensearch_client,
        )
        return create_opensearch_client(
            endpoint=endpoint,
            region=region,
            service=service,
        )
    except Exception as exc:
        raise SupplierAnalysisProviderError(
            "Unable to configure Amazon OpenSearch retrieval."
        ) from exc


@lru_cache
def _build_policy_retriever(
    endpoint: str,
    region: str,
    service: str,
    index_name: str,
    embedding_model_id: str,
    embedding_dimensions: int,
) -> PolicyRetriever:
    from backend.app.infrastructure.retrieval.opensearch.policy_retriever import (
        OpenSearchPolicyRetriever,
    )

    client = _build_opensearch_client(endpoint, region, service)
    embedding_provider = _build_embedding_provider(
        region,
        embedding_model_id,
        embedding_dimensions,
    )
    return OpenSearchPolicyRetriever(
        client=client,
        embedding_provider=embedding_provider,
        index_name=index_name,
    )


def get_policy_retriever(
    settings: Annotated[Settings, Depends(get_settings)],
) -> PolicyRetriever:
    if not settings.opensearch_endpoint:
        return NullPolicyRetriever()

    return _build_policy_retriever(
        settings.opensearch_endpoint,
        settings.aws_region,
        settings.opensearch_service,
        settings.opensearch_index_name,
        settings.embedding_model_id,
        settings.embedding_dimensions,
    )


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
