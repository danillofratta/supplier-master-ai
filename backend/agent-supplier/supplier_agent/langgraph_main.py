import asyncio
from uuid import uuid4

from langgraph.types import Command

from supplier_agent.langgraph_agent import build_agent


async def main() -> None:
    agent = await build_agent()

    config = {
        "configurable": {
            "thread_id": str(uuid4()),
        }
    }

    user_message = input(
        "\nWhat do you want the Supplier Agent to do?\n> "
    )

    result = await agent.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": user_message
                }
            ]
        },
        config=config,
        version="v2",
    )

    while result.interrupts:
        result = await _handle_interrupt(
            agent=agent,
            result=result,
            config=config,
        )

    final_message = result.value[
        "messages"
    ][-1]

    print()
    print("Agent response:")
    print(
        _extract_text(
            final_message
        )
    )

async def _handle_interrupt(
    agent,
    result,
    config,
):
    interrupt = result.interrupts[0]

    print()
    print("=" * 60)
    print("ACTION REQUIRES HUMAN APPROVAL")
    print("=" * 60)

    action_requests = interrupt.value[
        "action_requests"
    ]

    for action in action_requests:
        print()
        print(
            f"Tool: {action['name']}"
        )
        print(
            f"Arguments: {action['args']}"
        )

        if action.get("description"):
            print(
                f"Description: "
                f"{action['description']}"
            )

    answer = input(
        "\nDo you approve this action? [y/N]: "
    )

    approved = (
        answer.strip().lower()
        in {"y", "yes"}
    )

    decisions = []

    for _ in action_requests:
        if approved:
            decisions.append(
                {
                    "type": "approve",
                }
            )
        else:
            decisions.append(
                {
                    "type": "reject",
                    "message": (
                        "The user rejected this action. "
                        "Do not execute it."
                    ),
                }
            )

    result = await agent.ainvoke(
        Command(
            resume={
                "decisions": decisions,
            }
        ),
        config=config,
        version="v2",
    )

    _print_tool_results(result)

    return result

def _print_tool_results(result) -> None:
    messages = result.value.get(
        "messages",
        []
    )

    print()
    print("TOOL RESULTS AFTER APPROVAL")

    for message in messages:
        message_type = getattr(
            message,
            "type",
            None,
        )

        if message_type != "tool":
            continue

        print(
            f"Tool: {getattr(message, 'name', None)}"
        )
        print(
            f"Status: {getattr(message, 'status', None)}"
        )
        print(
            f"Content: {message.content}"
        )

def _extract_text(
    message,
) -> str:
    content = message.content

    if isinstance(content, str):
        return content

    return "\n".join(
        block["text"]
        for block in content
        if isinstance(block, dict)
        and block.get("type") == "text"
    )


if __name__ == "__main__":
    asyncio.run(main())