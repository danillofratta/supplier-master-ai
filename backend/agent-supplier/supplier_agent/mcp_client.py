from mcp import Client
from typing import Any

class SupplierMcpClient:
    def __init__(
        self,
        server_url: str,
    ) -> None:
        self._server_url = server_url

    async def get_tools(self):
        async with Client(self._server_url) as client:
            result = await client.list_tools()
            return result.tools

    async def call_tool(
        self,
        name: str,
        arguments: dict[str, Any],
    ) -> dict:
        async with Client(self._server_url) as client:
            result = await client.call_tool(name=name, arguments=arguments)

        if result.is_error:
            message = " ".join(
                getattr(item, "text", str(item))
                for item in result.content
            )

            return {
                "error": True,
                "message": message,
            }

        if result.structured_content is not None:
            return result.structured_content

        return {
            "result": " ".join(
                getattr(item, "text", str(item))
                for item in result.content
            )
        }