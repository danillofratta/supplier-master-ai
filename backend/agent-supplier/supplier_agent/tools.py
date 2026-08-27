import asyncio
from uuid import UUID, uuid4

from langchain_core.tools import BaseTool, StructuredTool
from pydantic import BaseModel, Field


class StartSupplierOnboardingInput(BaseModel):
    supplier_id: UUID = Field(
        description="Supplier identifier."
    )


class InvestigateSupplierInput(BaseModel):
    supplier_id: UUID = Field(
        description="Supplier identifier to investigate comprehensively."
    )


def _find_tool(
    tools: list[BaseTool],
    name: str,
) -> BaseTool:
    try:
        return next(
            tool
            for tool in tools
            if tool.name == name
        )
    except StopIteration as exc:
        raise RuntimeError(
            f"Required MCP tool '{name}' was not found."
        ) from exc


def prepare_tools(
    mcp_tools: list[BaseTool],
) -> list[BaseTool]:
    original_start_tool = _find_tool(
        mcp_tools,
        "start_supplier_onboarding",
    )
    get_supplier_tool = _find_tool(
        mcp_tools,
        "get_supplier",
    )
    analyze_supplier_tool = _find_tool(
        mcp_tools,
        "analyze_supplier",
    )
    onboarding_status_tool = _find_tool(
        mcp_tools,
        "get_onboarding_status",
    )

    async def start_supplier_onboarding(
        supplier_id: UUID,
    ):
        # Idempotency is a technical concern. The LLM deliberately does not
        # receive this argument in its tool schema.
        idempotency_key = uuid4()

        print(
            "[AGENT] Generated idempotency key:",
            idempotency_key,
        )

        return await original_start_tool.ainvoke(
            {
                "supplier_id": str(supplier_id),
                "idempotency_key": str(idempotency_key),
            }
        )

    async def investigate_supplier(
        supplier_id: UUID,
    ) -> dict:
        """Collect the three authoritative views used by an investigation."""

        supplier_id_text = str(supplier_id)

        supplier_task = get_supplier_tool.ainvoke(
            {"supplier_id": supplier_id_text}
        )
        analysis_task = analyze_supplier_tool.ainvoke(
            {"supplier_id": supplier_id_text}
        )
        onboarding_task = onboarding_status_tool.ainvoke(
            {"supplier_id": supplier_id_text}
        )

        supplier, analysis, onboarding = await asyncio.gather(
            supplier_task,
            analysis_task,
            onboarding_task,
            return_exceptions=True,
        )

        def normalize(value):
            if isinstance(value, Exception):
                return {
                    "available": False,
                    "error": str(value),
                }
            return {
                "available": True,
                "data": value,
            }

        return {
            "supplier_id": supplier_id_text,
            "master_data": normalize(supplier),
            "ai_analysis": normalize(analysis),
            "onboarding": normalize(onboarding),
        }

    wrapped_start_tool = StructuredTool.from_function(
        coroutine=start_supplier_onboarding,
        name="start_supplier_onboarding",
        description=(
            "Start the governed supplier onboarding workflow. "
            "Human approval is enforced by the application before execution."
        ),
        args_schema=StartSupplierOnboardingInput,
        handle_tool_error=True,
    )

    investigation_tool = StructuredTool.from_function(
        coroutine=investigate_supplier,
        name="investigate_supplier",
        description=(
            "Perform a comprehensive read-only supplier investigation by "
            "collecting master data, AI/RAG risk analysis, and persisted "
            "onboarding workflow state. Use this for full investigations."
        ),
        args_schema=InvestigateSupplierInput,
        handle_tool_error=True,
    )

    prepared = [
        (
            wrapped_start_tool
            if tool.name == "start_supplier_onboarding"
            else tool
        )
        for tool in mcp_tools
    ]

    return [*prepared, investigation_tool]
