from uuid import UUID

from mcp.server import MCPServer
from mcp.types import ToolAnnotations

from supplier_mcp.api_client import SupplierApiClient
from supplier_mcp.models import (
    OnboardingStatusResponse,
    PolicyIngestResponse,
    SupplierAnalysisResponse,
    SupplierResponse,
    SupplierListResponse,
    StartOnboardingResponse,
    SupplierReviewDecisionResponse,
)

api_client = SupplierApiClient(base_url="http://localhost:8000")

mcp = MCPServer(
    "Supplier Master MCP Server",
)

@mcp.tool()
async def health() -> str:
    """Health check endpoint for the Supplier Master MCP Server."""
    return await api_client.health()

@mcp.tool(
    title="Get Supplier",
    annotations=ToolAnnotations(
        read_only_hint=True,
        open_world_hint=False,
    ),
)
async def get_supplier(supplier_id: str) -> SupplierResponse:
    """
    Get a supplier by its identifier.
    """

    return await api_client.get_supplier(supplier_id=supplier_id)

@mcp.tool(
        title="Get List of Suppliers",
        annotations=ToolAnnotations(
            read_only_hint=True,
            open_world_hint=False,
        ),
)
async def get_suppliers() -> SupplierListResponse:
    """
    Get all suppliers.
    """

    return await api_client.get_suppliers()

@mcp.tool(
        title="Analyze Supplier",
        annotations=ToolAnnotations(
            read_only_hint=True,
            open_world_hint=False,
        ),
)
async def analyze_supplier(supplier_id: str) -> SupplierAnalysisResponse:
    """
    Analyze a supplier against corporate policies using RAG and AI.

    This tool only produces an analysis and recommendation.
    It does not start onboarding or synchronize the supplier with SAP.
    """

    return await api_client.analyze_supplier(supplier_id=supplier_id)

@mcp.tool(
        title="Get Supplier Onboarding Status",
        annotations=ToolAnnotations(
            read_only_hint=True,
            open_world_hint=False,
        ),
)
async def get_onboarding_status(supplier_id: str) -> OnboardingStatusResponse:
    """
    Get the current onboarding status for a supplier.

    This tool returns the current onboarding workflow, correlation ID, review and SAP status.
    """

    return await api_client.get_onboarding_status(supplier_id=supplier_id)

@mcp.resource(
    "supplier://{supplier_id}",
    mime_type="application/json",
)
async def supplier_resource(supplier_id: str) -> dict:
    supplier = await api_client.get_supplier(supplier_id=supplier_id)

    return supplier.model_dump(mode="json")

@mcp.resource(
    "supplier-onboarding://{supplier_id}",
    mime_type="application/json",
)
async def supplier_onboarding_resource(
    supplier_id: str,
) -> dict:
    """
    Current onboarding workflow state for a supplier.
    """

    onboarding = await api_client.get_onboarding_status(
        supplier_id=supplier_id
    )

    return onboarding.model_dump(
        mode="json"
    )

@mcp.prompt()
def investigate_supplier(
    supplier_id: str,
) -> str:
    """
    Investigate the current state of a supplier.
    """

    return f"""
        Investigate supplier {supplier_id}.

        1. Retrieve the supplier information.
        2. Review its current status.
        3. Identify missing or suspicious information.
        4. Summarize the current situation.
        5. Recommend the next action.

        Do not modify the supplier.
        """

@mcp.tool(
        title="Start Supplier Onboarding",
        annotations=ToolAnnotations(
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=True,
        ),
)
async def start_supplier_onboarding(
    supplier_id: str,
    idempotency_key: UUID
) -> StartOnboardingResponse:
    """
    Start the governed supplier onboarding workflow.

    This operation changes system state and may initiate
    human review and SAP synchronization.
    """

    return await api_client.start_onboarding(
        supplier_id=supplier_id,
        idempotency_key=idempotency_key
    )

@mcp.tool(
        title="Approve Supplier Review",
        annotations=ToolAnnotations(
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=False,
            open_world_hint=True,
        ),
)
async def approve_supplier_review(
    supplier_id: str
) -> SupplierReviewDecisionResponse:
    """
    Approve a supplier that is waiting for human review.

    Approval changes workflow state and may schedule
    synchronization with SAP. Human approval is enforced by
    the agent runtime when this tool is used through LangGraph.
    """

    return await api_client.decide_supplier_review(
        supplier_id=supplier_id,
        decision="approve",
    )

@mcp.tool(
        title="Reject Supplier Review",
        annotations=ToolAnnotations(
            read_only_hint=False,
            destructive_hint=True,
            idempotent_hint=False,
            open_world_hint=False,
        ),
)
async def reject_supplier_review(
    supplier_id: str,
    reason: str
) -> SupplierReviewDecisionResponse:
    """
    Reject a supplier that is waiting for human review.

    Rejection stops the current onboarding workflow.
    A business rejection reason is required. Human approval is
    enforced by the agent runtime when used through LangGraph.
    """

    return await api_client.decide_supplier_review(
        supplier_id=supplier_id,
        decision="reject",
        reason=reason,
    )

@mcp.tool(
    title="Ingest Supplier Policy ",
    annotations=ToolAnnotations(
        read_only_hint=False,
        destructive_hint=True,
        idempotent_hint=False,
        open_world_hint=False,
    ),
)
async def ingest_supplier_policy(
    document_id: str,
    title: str,
    content: str,
    policy_type: str,
    version: str,
    effective_date: str,
) -> PolicyIngestResponse:
    """
    Ingest or replace a supplier policy in the AI knowledge base.

    The policy is chunked, embedded and indexed for use by
    supplier RAG analysis.

    This operation changes the AI knowledge base. Human approval
    is enforced by the agent runtime when used through LangGraph.
    """

    return await api_client.ingest_policy(
        document_id=document_id,
        title=title,
        content=content,
        policy_type=policy_type,
        version=version,
        effective_date=effective_date,
    )

if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host="127.0.0.1",
        port=8010,
        streamable_http_path="/mcp",
        stateless_http=True,
        json_response=True,
    )