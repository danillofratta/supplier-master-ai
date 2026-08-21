from typing import Annotated

from fastapi import APIRouter, Depends, status

from api_supplier.bootstrap.dependencies import get_ingest_policy_handler
from api_supplier.features.policies.ingest.command import IngestPolicyCommand
from api_supplier.features.policies.ingest.handler import IngestPolicyHandler
from api_supplier.features.policies.ingest.models import IngestPolicyRequest, IngestPolicyResponse

router = APIRouter(prefix="/v1/policies", tags=["Policies"])


@router.post("/ingest", response_model=IngestPolicyResponse, status_code=status.HTTP_201_CREATED)
async def ingest_policy(
    request: IngestPolicyRequest,
    handler: Annotated[IngestPolicyHandler, Depends(get_ingest_policy_handler)],
) -> IngestPolicyResponse:
    result = await handler.handle(
        IngestPolicyCommand(
            document_id=request.document_id,
            title=request.title,
            content=request.content,
            policy_type=request.policy_type,
            version=request.version,
            effective_date=request.effective_date,
        )
    )
    return IngestPolicyResponse(
        document_id=result.document_id,
        chunks_indexed=result.chunks_indexed,
        embedding_dimensions=result.embedding_dimensions,
    )
