from typing import Any, Literal

from pydantic import BaseModel, Field


class AgentMessageRequest(BaseModel):
    message: str = Field(min_length=1, max_length=12000)


class ApprovalDecisionRequest(BaseModel):
    decision: Literal["approve", "reject"]
    message: str | None = Field(default=None, max_length=2000)


class AgentChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class PendingAction(BaseModel):
    name: str
    arguments: dict[str, Any]
    description: str | None = None


class AgentRunResponse(BaseModel):
    thread_id: str
    status: Literal["completed", "pending_approval"]
    message: str | None = None
    pending_actions: list[PendingAction] = Field(default_factory=list)
    history: list[AgentChatMessage] = Field(default_factory=list)


class CreateThreadResponse(BaseModel):
    thread_id: str
