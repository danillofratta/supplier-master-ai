import { type FormEvent, useState } from "react";
import { ingestPolicy } from "../api/policiesApi";
import type { IngestPolicyResponse } from "../models/supplier";
import { getApiErrorMessage } from "../api/apiError";

export function IngestPolicyPage() {
  const [form, setForm] = useState({
    document_id: "",
    title: "",
    policy_type: "supplier_onboarding",
    version: "1.0",
    effective_date: new Date().toISOString().slice(0, 10),
    content: "",
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<IngestPolicyResponse | null>(null);

  function update(name: string, value: string) {
    setForm((current) => ({ ...current, [name]: value }));
  }

  async function submit(event: FormEvent) {
    event.preventDefault();
    setSaving(true);
    setError(null);
    setResult(null);
    try {
      setResult(await ingestPolicy(form));
    } catch (error: unknown) {
      setError(
        getApiErrorMessage(
          error,
          "Unable to ingest policy."
        )
      );
    } finally {
      setSaving(false);
    }
  }

  return (
    <>
      <div className="page-heading">
        <div>
          <span className="eyebrow">RAG knowledge base</span>
          <h1>Ingest policy</h1>
          <p>Chunk, embed with Bedrock and index supplier policies in OpenSearch.</p>
        </div>
      </div>

      {error && <div className="callout callout-error">{error}</div>}
      {result && (
        <div className="callout callout-success">
          Policy <strong>{result.document_id}</strong> indexed successfully — {result.chunks_indexed} chunks, {result.embedding_dimensions} dimensions.
        </div>
      )}

      <form className="panel policy-form" onSubmit={submit}>
        <div className="form-grid">
          <label>Document ID<input value={form.document_id} onChange={(e) => update("document_id", e.target.value)} required /></label>
          <label>Title<input value={form.title} onChange={(e) => update("title", e.target.value)} required /></label>
          <label>Policy type<input value={form.policy_type} onChange={(e) => update("policy_type", e.target.value)} required /></label>
          <label>Version<input value={form.version} onChange={(e) => update("version", e.target.value)} required /></label>
          <label>Effective date<input type="date" value={form.effective_date} onChange={(e) => update("effective_date", e.target.value)} required /></label>
        </div>
        <label>Load text/markdown file<input type="file" accept=".txt,.md,text/plain,text/markdown" onChange={async (e) => { const file = e.target.files?.[0]; if (file) update("content", await file.text()); }} /></label>
        <label className="policy-content">Policy content<textarea rows={18} value={form.content} onChange={(e) => update("content", e.target.value)} required placeholder="Paste the supplier onboarding/compliance policy here..." /></label>
        <div className="form-actions"><button className="button primary" disabled={saving}>{saving ? "Ingesting..." : "Ingest policy"}</button></div>
      </form>
    </>
  );
}
