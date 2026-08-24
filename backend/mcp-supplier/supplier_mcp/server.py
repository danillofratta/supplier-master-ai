from uuid import UUID

from mcp.server import MCPServer
from mcp.types import ToolAnnotations

from supplier_mcp.exceptions import (
    ConfirmationRequiredError,
)
from supplier_mcp.api_client import SupplierApiClient
from supplier_mcp.models import (
    OnboardingStatusResponse,
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
    idempotency_key: UUID,
    confirmed: bool = False,
) -> StartOnboardingResponse:
    """
    Start the governed supplier onboarding workflow.

    This operation changes system state and may initiate
    human review and SAP synchronization.

    Set confirmed=true only after explicit user approval.
    """

    if not confirmed:
        raise ConfirmationRequiredError(
            "Starting supplier onboarding changes system state "
            "and may initiate human review and SAP synchronization. "
            "Explicit confirmation is required."
        )

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
    supplier_id: str,
    confirmed: bool = False,
) -> SupplierReviewDecisionResponse:
    """
    Approve a supplier that is waiting for human review.

    Approval changes workflow state and may schedule
    synchronization with SAP.

    Explicit user confirmation is required.
    """

    if not confirmed:
        raise ConfirmationRequiredError(
            "Approving supplier review changes system state "
            "and may initiate SAP synchronization. "
            "Explicit confirmation is required."
        )

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
    reason: str,
    confirmed: bool = False,
) -> SupplierReviewDecisionResponse:
    """
    Reject a supplier that is waiting for human review.

    Rejection stops the current onboarding workflow.

    A reason and explicit user confirmation are required.
    """"

    if not confirmed:
        raise ConfirmationRequiredError(
            "Rejecting supplier review changes system state "
            "and may initiate SAP synchronization. "
            "Explicit confirmation is required."
        )

    return await api_client.decide_supplier_review(
        supplier_id=supplier_id,
        decision="reject",
        reason=reason,
    )

