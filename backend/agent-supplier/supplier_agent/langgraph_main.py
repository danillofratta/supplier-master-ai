import asyncio
import sys
from uuid import uuid4

from langgraph.types import Command

from supplier_agent.langgraph_agent import build_agent
from langgraph.checkpoint.postgres.aio import (
    AsyncPostgresSaver,
)

from supplier_agent.settings import (
    get_settings,
)


async def main() -> None:
    settings = get_settings()

    connection_string = settings.langgraph_database_url

    async with AsyncPostgresSaver.from_conn_string(
        connection_string
    ) as checkpointer:

        await checkpointer.setup()

        agent = await build_agent(
            checkpointer
        )

        await run_cli(agent)

async def run_cli(agent) -> None:
    thread_id = _get_thread_id()

    config = {
        "configurable": {
            "thread_id": thread_id,
        }
    }

    state = await agent.aget_state(
        config
    )

    pending_interrupts = [
        interrupt
        for task in state.tasks
        for interrupt in task.interrupts
    ]    

    if pending_interrupts:
        print()
        print(
            "This conversation has a pending approval."
        )

        result = await _resume_pending_interrupt(
            agent=agent,
            config=config,
            interrupts=pending_interrupts,
        )

        if result is not None:
            final_message = result.value[
                "messages"
            ][-1]

            print()
            print("Agent:")
            print(
                _extract_text(
                    final_message
                )
            )    

    print()
    print("Supplier Master AI Agent")
    print(f"Thread ID: {thread_id}")
    print("Type 'exit' to quit.")

    while True:
        user_message = input("\n> ").strip()

        if user_message.lower() in {
            "exit",
            "quit",
        }:
            break

        if not user_message:
            continue

        result = await agent.ainvoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": user_message,
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
        print("Agent:")
        print(
            _extract_text(
                final_message
            )
        )        

async def _resume_pending_interrupt(
    agent,
    config,
    interrupts,
):
    interrupt = interrupts[0]

    print()
    print("=" * 60)
    print("PENDING HUMAN APPROVAL")
    print("=" * 60)
    print(interrupt.value)

    answer = input(
        "\nDo you approve this action? [y/N]: "
    )

    approved = (
        answer.strip().lower()
        in {"y", "yes"}
    )

    decision = (
        {
            "type": "approve",
        }
        if approved
        else {
            "type": "reject",
            "message": (
                "The user rejected this action."
            ),
        }
    )

    return await agent.ainvoke(
        Command(
            resume={
                "decisions": [
                    decision
                ]
            }
        ),
        config=config,
        version="v2",
    )        

def _get_thread_id() -> str:
    print()
    print("Conversation")
    print("1 - New conversation")
    print("2 - Resume conversation")

    option = input("> ").strip()

    if option == "2":
        thread_id = input(
            "Thread ID: "
        ).strip()

        if thread_id:
            return thread_id

    return str(uuid4())        

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
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(
            asyncio.WindowsSelectorEventLoopPolicy()
        )

    asyncio.run(main())