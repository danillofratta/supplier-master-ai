import asyncio
import sys

import uvicorn

from supplier_agent.settings import get_settings


def main() -> None:
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(
            asyncio.WindowsSelectorEventLoopPolicy()
        )

    settings = get_settings()

    uvicorn.run(
        "supplier_agent.api:app",
        host=settings.agent_api_host,
        port=settings.agent_api_port,
        reload=False,
        loop="asyncio",
    )


if __name__ == "__main__":
    main()
