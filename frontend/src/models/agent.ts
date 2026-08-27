export type AgentStatus =
  | "completed"
  | "pending_approval";

export interface AgentChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface PendingAgentAction {
  name: string;
  arguments: Record<string, unknown>;
  description?: string | null;
}

export interface AgentRunResponse {
  thread_id: string;
  status: AgentStatus;
  message?: string | null;
  pending_actions: PendingAgentAction[];
  history: AgentChatMessage[];
}

export interface CreateAgentThreadResponse {
  thread_id: string;
}
