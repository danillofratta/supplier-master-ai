import {
  type FormEvent,
  useEffect,
  useRef,
  useState,
} from "react";
import { useSearchParams } from "react-router-dom";
import {
  createAgentThread,
  decideAgentApproval,
  getAgentThread,
  investigateSupplierWithAgent,
  sendAgentMessage,
} from "../api/agentApi";
import { getApiErrorMessage } from "../api/apiError";
import type {
  AgentChatMessage,
  AgentRunResponse,
  PendingAgentAction,
} from "../models/agent";

const THREAD_STORAGE_KEY = "supplier-master-agent-thread-id";

export function AgentPage() {
  const [searchParams] = useSearchParams();
  const supplierFromQuery = searchParams.get("supplierId") ?? "";

  const [threadId, setThreadId] = useState("");
  const [messages, setMessages] = useState<AgentChatMessage[]>([]);
  const [pendingActions, setPendingActions] = useState<PendingAgentAction[]>([]);
  const [message, setMessage] = useState("");
  const [supplierId, setSupplierId] = useState(supplierFromQuery);
  const [approvalNote, setApprovalNote] = useState("");
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const chatEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    void initialize();
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, pendingActions]);

  function applyResponse(response: AgentRunResponse) {
    setThreadId(response.thread_id);
    setMessages(response.history);
    setPendingActions(response.pending_actions);
  }

  async function initialize() {
    setLoading(true);
    setError(null);

    try {
      const storedThreadId = window.localStorage.getItem(
        THREAD_STORAGE_KEY
      );

      if (storedThreadId) {
        const response = await getAgentThread(storedThreadId);
        applyResponse(response);
        setLoading(false);
        return;
      }

      await startNewConversation();
    } catch (error: unknown) {
      setError(
        getApiErrorMessage(
          error,
          "Unable to connect to the Supplier AI Agent API."
        )
      );
      setLoading(false);
    }
  }

  async function startNewConversation() {
    setSending(true);
    setError(null);

    try {
      const newThreadId = await createAgentThread();
      window.localStorage.setItem(
        THREAD_STORAGE_KEY,
        newThreadId
      );
      setThreadId(newThreadId);
      setMessages([]);
      setPendingActions([]);
      setApprovalNote("");
    } catch (error: unknown) {
      setError(
        getApiErrorMessage(
          error,
          "Unable to create an agent conversation."
        )
      );
    } finally {
      setSending(false);
      setLoading(false);
    }
  }

  async function submitMessage(event: FormEvent) {
    event.preventDefault();

    const text = message.trim();
    if (!text || !threadId || pendingActions.length > 0) {
      return;
    }

    setSending(true);
    setError(null);

    try {
      const response = await sendAgentMessage(threadId, text);
      applyResponse(response);
      setMessage("");
    } catch (error: unknown) {
      setError(
        getApiErrorMessage(
          error,
          "The agent could not process this message."
        )
      );
    } finally {
      setSending(false);
    }
  }

  async function investigate() {
    const id = supplierId.trim();
    if (!id || !threadId || pendingActions.length > 0) {
      return;
    }

    setSending(true);
    setError(null);

    try {
      const response = await investigateSupplierWithAgent(
        threadId,
        id
      );
      applyResponse(response);
    } catch (error: unknown) {
      setError(
        getApiErrorMessage(
          error,
          "Unable to investigate this supplier."
        )
      );
    } finally {
      setSending(false);
    }
  }

  async function decide(
    decision: "approve" | "reject"
  ) {
    if (!threadId || pendingActions.length === 0) {
      return;
    }

    setSending(true);
    setError(null);

    try {
      const response = await decideAgentApproval(
        threadId,
        decision,
        approvalNote.trim() || undefined
      );
      applyResponse(response);
      setApprovalNote("");
    } catch (error: unknown) {
      setError(
        getApiErrorMessage(
          error,
          "Unable to apply the human approval decision."
        )
      );
    } finally {
      setSending(false);
    }
  }

  if (loading) {
    return <div className="empty-state">Loading AI Agent...</div>;
  }

  return (
    <>
      <div className="page-heading">
        <div>
          <span className="eyebrow">Agentic AI operations</span>
          <h1>Supplier AI Agent</h1>
          <p>
            Investigate suppliers, use MCP capabilities and govern write
            operations with persistent Human-in-the-Loop approval.
          </p>
        </div>

        <button
          className="button secondary"
          onClick={() => void startNewConversation()}
          disabled={sending}
        >
          New conversation
        </button>
      </div>

      {error && (
        <div className="callout callout-error">{error}</div>
      )}

      <div className="agent-layout">
        <section className="panel agent-chat-panel">
          <div className="agent-thread-meta">
            <div>
              <span>Persistent LangGraph thread</span>
              <code>{threadId}</code>
            </div>
            <span className="agent-runtime-badge">
              MCP · HITL · PostgreSQL
            </span>
          </div>

          <div className="agent-messages">
            {messages.length === 0 ? (
              <div className="agent-empty-state">
                <strong>Ask the Supplier Agent</strong>
                <p>
                  Try “Investigate supplier …”, “What is its onboarding
                  status?” or a governed action such as “Start onboarding”.
                </p>
              </div>
            ) : (
              messages.map((item, index) => (
                <article
                  key={`${item.role}-${index}`}
                  className={`agent-message agent-message-${item.role}`}
                >
                  <span>
                    {item.role === "user" ? "You" : "Supplier Agent"}
                  </span>
                  <p>{item.content}</p>
                </article>
              ))
            )}

            {pendingActions.length > 0 && (
              <section className="agent-approval-card">
                <div>
                  <span className="eyebrow">Human-in-the-Loop</span>
                  <h3>Action requires approval</h3>
                  <p>
                    The LangGraph execution is paused in PostgreSQL. No
                    state-changing tool is executed until you approve it.
                  </p>
                </div>

                {pendingActions.map((action, index) => (
                  <div
                    className="agent-action-request"
                    key={`${action.name}-${index}`}
                  >
                    <strong>{action.name}</strong>
                    {action.description && <p>{action.description}</p>}
                    <pre>
                      {JSON.stringify(action.arguments, null, 2)}
                    </pre>
                  </div>
                ))}

                <label className="agent-approval-note">
                  Review note (optional)
                  <input
                    value={approvalNote}
                    onChange={(event) =>
                      setApprovalNote(event.target.value)
                    }
                    placeholder="Reason for rejecting or audit note"
                  />
                </label>

                <div className="action-row">
                  <button
                    className="button"
                    disabled={sending}
                    onClick={() => void decide("reject")}
                  >
                    Reject action
                  </button>
                  <button
                    className="button primary"
                    disabled={sending}
                    onClick={() => void decide("approve")}
                  >
                    Approve action
                  </button>
                </div>
              </section>
            )}

            <div ref={chatEndRef} />
          </div>

          <form className="agent-composer" onSubmit={submitMessage}>
            <textarea
              rows={3}
              value={message}
              onChange={(event) => setMessage(event.target.value)}
              placeholder={
                pendingActions.length > 0
                  ? "Resolve the pending approval before sending a new message."
                  : "Ask the agent about a supplier or request an operation..."
              }
              disabled={sending || pendingActions.length > 0}
            />
            <button
              className="button primary"
              disabled={
                sending ||
                !message.trim() ||
                pendingActions.length > 0
              }
            >
              {sending ? "Working..." : "Send"}
            </button>
          </form>
        </section>

        <aside className="panel agent-side-panel">
          <span className="eyebrow">Investigation</span>
          <h2>Full supplier review</h2>
          <p>
            Runs the read-only investigation capability across master data,
            RAG risk analysis and persisted onboarding state.
          </p>

          <label>
            Supplier ID
            <input
              value={supplierId}
              onChange={(event) => setSupplierId(event.target.value)}
              placeholder="UUID"
            />
          </label>

          <button
            className="button primary"
            disabled={
              sending ||
              !supplierId.trim() ||
              pendingActions.length > 0
            }
            onClick={() => void investigate()}
          >
            Investigate supplier
          </button>

          <div className="agent-capabilities">
            <h3>Capabilities</h3>
            <ul>
              <li>Supplier master-data lookup</li>
              <li>RAG + AI risk assessment</li>
              <li>Onboarding state investigation</li>
              <li>Governed onboarding actions</li>
              <li>Human review approval/rejection</li>
              <li>Persistent conversations and approvals</li>
            </ul>
          </div>
        </aside>
      </div>
    </>
  );
}
