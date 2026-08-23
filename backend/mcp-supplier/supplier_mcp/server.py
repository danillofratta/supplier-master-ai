from mcp.server import MCPServer
from supplier_mcp.api_client import SupplierApiClient
from supplier_mcp.models import (
    OnboardingStatusResponse,
    SupplierAnalysisResponse,
    SupplierResponse,
    SupplierListResponse,
)

api_client = SupplierApiClient(base_url="http://localhost:8000")

mcp = MCPServer(
    "Supplier Master MCP Server",
)

@mcp.tool()
async def health() -> str:
    """Health check endpoint for the Supplier Master MCP Server."""
    return await api_client.health()

@mcp.tool()
async def get_supplier(supplier_id: str) -> SupplierResponse:
    """
    Get a supplier by its identifier.
    """

    return await api_client.get_supplier(supplier_id=supplier_id)

@mcp.tool()
async def get_suppliers() -> SupplierListResponse:
    """
    Get all suppliers.
    """

    return await api_client.get_suppliers()

@mcp.tool()
async def analyze_supplier(supplier_id: str) -> SupplierAnalysisResponse:
    """
    Analyze a supplier against corporate policies using RAG and AI.

    This tool only produces an analysis and recommendation.
    It does not start onboarding or synchronize the supplier with SAP.
    """

    return await api_client.analyze_supplier(supplier_id=supplier_id)

@mcp.tool()
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

