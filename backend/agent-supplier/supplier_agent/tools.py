from uuid import UUID, uuid4

from langchain_core.tools import BaseTool, StructuredTool
from pydantic import BaseModel, Field
from langchain_core.tools import (
    BaseTool,
    StructuredTool,
    ToolException,
)


class StartSupplierOnboardingInput(BaseModel):
    supplier_id: UUID = Field(
        description="Supplier identifier."
    )


def prepare_tools(
    mcp_tools: list[BaseTool],
) -> list[BaseTool]:
    original_start_tool = next(
        tool
        for tool in mcp_tools
        if tool.name == "start_supplier_onboarding"
    )

    async def start_supplier_onboarding(
        supplier_id: UUID,
    ):
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

    wrapped_start_tool = (
        StructuredTool.from_function(
            coroutine=start_supplier_onboarding,
            name="start_supplier_onboarding",
            description=(
                "Start the governed supplier onboarding workflow. "
            ),
            args_schema=StartSupplierOnboardingInput,
            handle_tool_error=True,
        )
    )

    return [
        (
            wrapped_start_tool
            if tool.name
            == "start_supplier_onboarding"
            else tool
        )
        for tool in mcp_tools
    ]