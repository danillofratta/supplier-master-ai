import asyncio

import boto3


class BedrockAgentClient:
    def __init__(
        self,
        region_name: str,
        model_id: str,
    ) -> None:
        self._model_id = model_id

        self._client = boto3.client(
            "bedrock-runtime",
            region_name=region_name,
        )

    def _build_tool_config(
        self,
        mcp_tools,
    ) -> dict:
        return {
            "tools": [
                {
                    "toolSpec": {
                        "name": tool.name,
                        "description": (
                            tool.description
                            or tool.name
                        ),
                        "inputSchema": {
                            "json": tool.input_schema,
                        },
                    }
                }
                for tool in mcp_tools
            ]
        }

    async def converse(
        self,
        messages: list[dict],
        mcp_tools,
    ) -> dict:
        return await asyncio.to_thread(
            self._client.converse,
            modelId=self._model_id,
            messages=messages,
            system=[
                {
                    "text": (
                        "You are the Supplier Master AI Agent."

                        "Use MCP tools as the source of truth."

                        "Rules:"

                        "1. Never infer onboarding state from supplier status. "
                        "Supplier status and onboarding workflow status are "
                        "separate concepts."

                        "2. Never invent system capabilities or business operations."

                        "3. Only recommend write operations that are actually "
                        "available through the provided tools."

                        "4. Never recommend approve_supplier_review or "
                        "reject_supplier_review unless the onboarding workflow "
                        "is currently waiting for human review."

                        "5. Never recommend start_supplier_onboarding when an "
                        "onboarding workflow is already active or completed, "
                        "unless the system explicitly indicates that a new "
                        "onboarding is allowed."

                        "6. When two tool results conflict, explicitly report the "
                        "inconsistency. Do not choose one by guessing."

                        "7. AI analysis is a recommendation. Persisted workflow "
                        "state is the source of truth for workflow execution."

                        "8. Never claim an operation was executed unless a tool "
                        "result confirms that execution."

                        "9. Never execute state-changing tools without the "
                        "application's explicit confirmation flow."
                    )
                }
            ],
            toolConfig=self._build_tool_config(
                mcp_tools
            ),
            inferenceConfig={
                "maxTokens": 1000,
                "temperature": 0.1,
            },
        )