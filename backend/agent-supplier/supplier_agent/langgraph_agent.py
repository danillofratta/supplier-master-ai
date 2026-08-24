import os

from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain_aws import ChatBedrockConverse
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.checkpoint.memory import InMemorySaver


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
- Never recommend approve_supplier_review or reject_supplier_review unless
  the onboarding workflow is waiting for human review.
- Never recommend starting onboarding when a completed or active workflow
  already exists unless the backend explicitly allows it.
"""


async def build_agent():
    mcp_client = MultiServerMCPClient(
        {
            "supplier": {
                "transport": "http",
                "url": "http://127.0.0.1:8010/mcp",
            }
        }
    )

    tools = await mcp_client.get_tools()

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