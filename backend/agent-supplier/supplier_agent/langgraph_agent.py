from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain_mcp_adapters.client import MultiServerMCPClient

from supplier_agent.model_factory import build_chat_model
from supplier_agent.settings import get_settings
from supplier_agent.tools import prepare_tools


SYSTEM_PROMPT = """
You are the Supplier Master AI Agent.

Use the available MCP-backed tools as the source of truth.

Rules:

- Never infer onboarding state from supplier status.
- Supplier status and onboarding workflow status are separate concepts.
- Do not invent system capabilities or business operations.
- AI analysis is a recommendation.
- Persisted workflow state is the source of truth for workflow execution.
- If tool results conflict, explicitly report the inconsistency instead of guessing.
- Never claim that an operation was executed unless a tool result confirms it.
- For a comprehensive investigation, prefer the investigate_supplier tool.
- Separate facts from AI recommendations in investigation summaries.
- If one investigation source is unavailable, report that limitation explicitly.
- Never suggest creating a new supplier, resetting/deleting a workflow, changing
  supplier status, or another operation unless that capability exists in tools.

- Do NOT ask the user for confirmation yourself before requesting a tool.
- If the user requests a state-changing operation, issue the appropriate tool call.
- Human approval for state-changing tools is handled by the application through
  HumanInTheLoopMiddleware.
- Do not set, simulate, or infer human approval in your response.

- If a state-changing tool fails, never call that tool again automatically.
- Report the tool failure to the user and stop.
- A retry of a state-changing operation requires a new explicit user request.
- A timeout or HTTP 5xx response from a state-changing tool does not prove that
  the operation did not happen. Report the outcome as uncertain when appropriate.
"""


async def build_agent(checkpointer):
    settings = get_settings()

    mcp_client = MultiServerMCPClient(
        {
            "supplier": {
                "transport": "http",
                "url": settings.supplier_mcp_url,
            }
        },
        handle_tool_errors=False,
    )

    mcp_tools = await mcp_client.get_tools()
    tools = prepare_tools(mcp_tools)
    model = build_chat_model(settings)

    return create_agent(
        model=model,
        tools=tools,
        system_prompt=SYSTEM_PROMPT,
        middleware=[
            HumanInTheLoopMiddleware(
                interrupt_on={
                    "start_supplier_onboarding": {
                        "allowed_decisions": [
                            "approve",
                            "reject",
                        ]
                    },
                    "approve_supplier_review": {
                        "allowed_decisions": [
                            "approve",
                            "reject",
                        ]
                    },
                    "reject_supplier_review": {
                        "allowed_decisions": [
                            "approve",
                            "reject",
                        ]
                    },
                    "ingest_supplier_policy": {
                        "allowed_decisions": [
                            "approve",
                            "reject",
                        ]
                    },
                },
                description_prefix=(
                    "Supplier Master action requires human approval"
                ),
            ),
        ],
        checkpointer=checkpointer,
    )
