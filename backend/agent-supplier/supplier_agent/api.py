from contextlib import asynccontextmanager
from typing import Any
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.types import Command

from supplier_agent.api_models import (
    AgentChatMessage,
    AgentMessageRequest,
    AgentRunResponse,
    ApprovalDecisionRequest,
    CreateThreadResponse,
    PendingAction,
)
from supplier_agent.langgraph_agent import build_agent
from supplier_agent.settings import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()

    async with AsyncPostgresSaver.from_conn_string(
        settings.langgraph_database_url
    ) as checkpointer:
        await checkpointer.setup()
        app.state.agent = await build_agent(checkpointer)
        yield


settings = get_settings()
app = FastAPI(
    title="Supplier Master AI Agent API",
    version="0.1.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _config(thread_id: str) -> dict:
    return {
        "configurable": {
            "thread_id": thread_id,
        }
    }


def _extract_text(message: Any) -> str:
    content = getattr(message, "content", "")

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        return "\n".join(
            block["text"]
            for block in content
            if isinstance(block, dict)
            and block.get("type") == "text"
            and isinstance(block.get("text"), str)
        )

    return str(content or "")


def _history_from_values(values: dict | None) -> list[AgentChatMessage]:
    if not values:
        return []

    history: list[AgentChatMessage] = []

    for message in values.get("messages", []):
        message_type = getattr(message, "type", None)
        text = _extract_text(message).strip()

        if not text:
            continue

        if message_type == "human":
            history.append(
                AgentChatMessage(
                    role="user",
                    content=text,
                )
            )
        elif message_type == "ai":
            history.append(
                AgentChatMessage(
                    role="assistant",
                    content=text,
                )
            )

    return history


def _pending_actions(interrupts) -> list[PendingAction]:
    actions: list[PendingAction] = []

    for interrupt in interrupts:
        value = interrupt.value
        if not isinstance(value, dict):
            continue

        for action in value.get("action_requests", []):
            actions.append(
                PendingAction(
                    name=action.get("name", "unknown"),
                    arguments=(
                        action.get("arguments")
                        or action.get("args")
                        or {}
                    ),
                    description=action.get("description"),
                )
            )

    return actions


def _interrupts_from_state(state) -> list:
    return [
        interrupt
        for task in state.tasks
        for interrupt in task.interrupts
    ]


def _response_from_result(
    thread_id: str,
    result,
) -> AgentRunResponse:
    values = result.value or {}
    history = _history_from_values(values)

    if result.interrupts:
        return AgentRunResponse(
            thread_id=thread_id,
            status="pending_approval",
            pending_actions=_pending_actions(result.interrupts),
            history=history,
        )

    message = None
    messages = values.get("messages", [])
    if messages:
        message = _extract_text(messages[-1]).strip() or None

    return AgentRunResponse(
        thread_id=thread_id,
        status="completed",
        message=message,
        history=history,
    )


async def _run_message(
    request: Request,
    thread_id: str,
    message: str,
) -> AgentRunResponse:
    agent = request.app.state.agent
    config = _config(thread_id)
    state = await agent.aget_state(config)

    if _interrupts_from_state(state):
        raise HTTPException(
            status_code=409,
            detail=(
                "This thread has a pending human approval. "
                "Resolve it before sending another message."
            ),
        )

    result = await agent.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": message,
                }
            ]
        },
        config=config,
        version="v2",
    )

    return _response_from_result(
        thread_id,
        result,
    )


@app.get("/health")
async def health() -> dict[str, str]:
    return {
        "status": "ok",
        "provider": settings.agent_ai_provider,
    }


@app.post(
    "/api/agent/threads",
    response_model=CreateThreadResponse,
)
async def create_thread() -> CreateThreadResponse:
    return CreateThreadResponse(
        thread_id=str(uuid4())
    )


@app.get(
    "/api/agent/threads/{thread_id}",
    response_model=AgentRunResponse,
)
async def get_thread(
    thread_id: UUID,
    request: Request,
) -> AgentRunResponse:
    thread_id_text = str(thread_id)
    agent = request.app.state.agent
    state = await agent.aget_state(
        _config(thread_id_text)
    )
    interrupts = _interrupts_from_state(state)
    history = _history_from_values(state.values)

    return AgentRunResponse(
        thread_id=thread_id_text,
        status=(
            "pending_approval"
            if interrupts
            else "completed"
        ),
        message=(
            history[-1].content
            if history
            and history[-1].role == "assistant"
            else None
        ),
        pending_actions=_pending_actions(interrupts),
        history=history,
    )


@app.post(
    "/api/agent/threads/{thread_id}/messages",
    response_model=AgentRunResponse,
)
async def send_message(
    thread_id: UUID,
    body: AgentMessageRequest,
    request: Request,
) -> AgentRunResponse:
    return await _run_message(
        request=request,
        thread_id=str(thread_id),
        message=body.message,
    )


@app.post(
    "/api/agent/threads/{thread_id}/investigate/{supplier_id}",
    response_model=AgentRunResponse,
)
async def investigate_supplier(
    thread_id: UUID,
    supplier_id: UUID,
    request: Request,
) -> AgentRunResponse:
    return await _run_message(
        request=request,
        thread_id=str(thread_id),
        message=(
            "Perform a comprehensive investigation of supplier "
            f"{supplier_id}. Use the comprehensive investigation capability. "
            "Separate master-data facts, AI/RAG assessment, persisted onboarding "
            "state, inconsistencies, and the recommended next action. Do not "
            "modify system state."
        ),
    )


@app.post(
    "/api/agent/threads/{thread_id}/approval",
    response_model=AgentRunResponse,
)
async def decide_pending_action(
    thread_id: UUID,
    body: ApprovalDecisionRequest,
    request: Request,
) -> AgentRunResponse:
    thread_id_text = str(thread_id)
    agent = request.app.state.agent
    config = _config(thread_id_text)
    state = await agent.aget_state(config)
    interrupts = _interrupts_from_state(state)

    if not interrupts:
        raise HTTPException(
            status_code=409,
            detail="This thread has no pending human approval.",
        )

    first_interrupt = interrupts[0]
    value = first_interrupt.value
    action_requests = (
        value.get("action_requests", [])
        if isinstance(value, dict)
        else []
    )

    if not action_requests:
        raise HTTPException(
            status_code=409,
            detail="The pending interrupt contains no actionable request.",
        )

    if body.decision == "approve":
        decisions = [
            {"type": "approve"}
            for _ in action_requests
        ]
    else:
        rejection_message = (
            body.message.strip()
            if body.message and body.message.strip()
            else "The user rejected this action. Do not execute it."
        )
        decisions = [
            {
                "type": "reject",
                "message": rejection_message,
            }
            for _ in action_requests
        ]

    result = await agent.ainvoke(
        Command(
            resume={
                "decisions": decisions,
            }
        ),
        config=config,
        version="v2",
    )

    return _response_from_result(
        thread_id_text,
        result,
    )
