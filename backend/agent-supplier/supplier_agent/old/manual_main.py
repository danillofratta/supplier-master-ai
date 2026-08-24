import asyncio
import os

from supplier_agent.agent import (
    SupplierAgent,
)
from supplier_agent.bedrock_client import (
    BedrockAgentClient,
)
from supplier_agent.mcp_client import (
    SupplierMcpClient,
)


async def main() -> None:
    mcp_client = SupplierMcpClient(
        server_url="http://127.0.0.1:8010/mcp"
    )

    bedrock_client = BedrockAgentClient(
        region_name=os.environ["AWS_REGION"],
        model_id=os.environ[
            "BEDROCK_MODEL_ID"
        ],
    )

    agent = SupplierAgent(
        mcp_client=mcp_client,
        bedrock_client=bedrock_client,
    )

    answer = await agent.run(
        "Investigate supplier "
        "80fef657-2254-4750-bacc-f308f833a71c. "
        "Tell me its supplier information, "
        "AI risk assessment, current onboarding status, "
        "and recommend the next action."
    )

    print()
    print("Agent response:")
    print(answer)

if __name__ == "__main__":
    asyncio.run(main())