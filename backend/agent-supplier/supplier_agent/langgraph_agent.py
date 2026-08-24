import os

from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain_aws import ChatBedrockConverse
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.checkpoint.memory import InMemorySaver
from supplier_agent.tools import (
    prepare_tools,
)


SYSTEM_PROMPT = """
You are the Supplier Master AI Agent.

Use the available MCP tools as the source of truth.

Rules:

- Never infer onboarding state from supplier status.
- Supplier status and onboarding workflow status are separate concepts.
- Do not invent system capabilities or business operations.
- AI analysis is a recommendation.
- Persisted workflow state is the source of truth for workflow execution.
- If tool results conflict, explicitly report the inconsistency instead of guessing.
- Never claim that an operation was executed unless a tool result confirms it.

- Do NOT ask the user for confirmation yourself before requesting a tool.
- If the user requests a state-changing operation, issue the appropriate tool call.
- Human approval for state-changing tools is handled by the application through HumanInTheLoopMiddleware.
- Do not set, simulate, or infer human approval in your response.

- If a state-changing tool fails, never call that tool again automatically.
- Report the tool failure to the user and stop.
- A retry of a state-changing operation requires a new explicit user request.
"""


async def build_agent():
    mcp_client = MultiServerMCPClient(
        {
            "supplier": {
                "transport": "http",
                "url": "http://127.0.0.1:8010/mcp",
            }
        },
        handle_tool_errors=False,
    )

    mcp_tools = await mcp_client.get_tools()

    tools = prepare_tools(
        mcp_tools
    )

    model = ChatBedrockConverse(
        model=os.environ["BEDROCK_MODEL_ID"],
        region_name=os.environ["AWS_REGION"],
        temperature=0.1,
        max_tokens=1500,
    )

    agent = create_agent(
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
        checkpointer=InMemorySaver(),
    )

    return agent