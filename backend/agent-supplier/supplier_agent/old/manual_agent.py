from typing import Any

from supplier_agent.bedrock_client import (
    BedrockAgentClient,
)
from supplier_agent.mcp_client import (
    SupplierMcpClient,
)


class SupplierAgent:
    def __init__(
        self,
        mcp_client: SupplierMcpClient,
        bedrock_client: BedrockAgentClient,
    ) -> None:
        self._mcp = mcp_client
        self._bedrock = bedrock_client

    async def run(
        self,
        user_message: str,
    ) -> str:
        tools = await self._mcp.get_tools()

        messages: list[dict[str, Any]] = [
            {
                "role": "user",
                "content": [
                    {
                        "text": user_message,
                    }
                ],
            }
        ]

        for _ in range(8):
            response = await self._bedrock.converse(
                messages=messages,
                mcp_tools=tools,
            )

            assistant_message = response[
                "output"
            ]["message"]

            messages.append(
                assistant_message
            )

            stop_reason = response[
                "stopReason"
            ]

            print(
                f"\n[AGENT] stop_reason={stop_reason}"
            )

            if stop_reason != "tool_use":
                return self._extract_text(
                    assistant_message
                )

            tool_results = []

            for block in assistant_message[
                "content"
            ]:
                tool_use = block.get(
                    "toolUse"
                )

                if tool_use is None:
                    continue

                result = await self._execute_tool(
                    tools=tools,
                    tool_use=tool_use,
                )

                tool_results.append(
                    {
                        "toolResult": {
                            "toolUseId": tool_use[
                                "toolUseId"
                            ],
                            "content": [
                                {
                                    "json": result,
                                }
                            ],
                        }
                    }
                )

            messages.append(
                {
                    "role": "user",
                    "content": tool_results,
                }
            )

        raise RuntimeError(
            "Maximum agent iterations reached."
        )

    async def _execute_tool(
        self,
        tools,
        tool_use: dict,
    ) -> dict:
        name = tool_use["name"]
        arguments = tool_use["input"]

        print(
            f"[AGENT] tool={name}"
        )

        print(
            f"[AGENT] arguments={arguments}"
        )        

        tool = next(
            (
                tool
                for tool in tools
                if tool.name == name
            ),
            None,
        )

        if tool is None:
            return {
                "error": True,
                "message": (
                    f"Unknown tool: {name}"
                ),
            }

        annotations = tool.annotations

        is_read_only = (
            annotations is not None
            and annotations.read_only_hint
            is True
        )

        if not is_read_only:
            return {
                "error": True,
                "message": (
                    f"Tool '{name}' changes system "
                    "state and requires an explicit "
                    "confirmation flow."
                ),
            }

        result = await self._mcp.call_tool(
            name=name,
            arguments=arguments,
        )

        print(
            f"[AGENT] Result: {result}"
        )    

        return result

    @staticmethod
    def _extract_text(
        message: dict,
    ) -> str:
        parts = [
            block["text"]
            for block in message["content"]
            if "text" in block
        ]

        return "\n".join(parts)