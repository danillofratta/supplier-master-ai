import axios from "axios";
import type {
  AgentRunResponse,
  CreateAgentThreadResponse,
} from "../models/agent";

const agentHttpClient = axios.create({
  baseURL:
    import.meta.env.VITE_AGENT_API_URL ??
    "http://localhost:8011/api",
  timeout: 120000,
  headers: {
    "Content-Type": "application/json",
  },
});

export async function createAgentThread(): Promise<string> {
  const response =
    await agentHttpClient.post<CreateAgentThreadResponse>(
      "/agent/threads"
    );

  return response.data.thread_id;
}

export async function getAgentThread(
  threadId: string
): Promise<AgentRunResponse> {
  const response =
    await agentHttpClient.get<AgentRunResponse>(
      `/agent/threads/${threadId}`
    );

  return response.data;
}

export async function sendAgentMessage(
  threadId: string,
  message: string
): Promise<AgentRunResponse> {
  const response =
    await agentHttpClient.post<AgentRunResponse>(
      `/agent/threads/${threadId}/messages`,
      { message }
    );

  return response.data;
}

export async function investigateSupplierWithAgent(
  threadId: string,
  supplierId: string
): Promise<AgentRunResponse> {
  const response =
    await agentHttpClient.post<AgentRunResponse>(
      `/agent/threads/${threadId}/investigate/${supplierId}`
    );

  return response.data;
}

export async function decideAgentApproval(
  threadId: string,
  decision: "approve" | "reject",
  message?: string
): Promise<AgentRunResponse> {
  const response =
    await agentHttpClient.post<AgentRunResponse>(
      `/agent/threads/${threadId}/approval`,
      {
        decision,
        message: message || undefined,
      }
    );

  return response.data;
}
