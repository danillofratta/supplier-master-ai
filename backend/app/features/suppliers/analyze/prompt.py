import json

from backend.app.domain.entities.supplier import Supplier
from backend.app.features.suppliers.analyze.policy_context import PolicyContext


SUPPLIER_ANALYSIS_PROMPT_VERSION = "supplier-analysis-prompt-v1"

SYSTEM_PROMPT = """
You are an enterprise supplier risk analysis assistant.

Your task is to analyze supplier information and provide a preliminary
recommendation.

You must not approve financial transactions or execute actions in external
systems.

Return only valid JSON. Do not include Markdown, explanations outside the
JSON object, or code fences.

The response must follow this schema:

{
  "risk_level": "low | medium | high",
  "recommended_action": "approve | human_review | reject",
  "missing_documents": ["string"],
  "policy_violations": ["string"],
  "summary": "string",
  "confidence": 0.0
}

Rules:

- confidence must be between 0 and 1;
- use human_review when information is incomplete;
- use human_review when confidence is below 0.80;
- do not invent supplier information;
- treat missing evidence as missing, not as valid;
- keep the summary concise.
""".strip()

def build_supplier_analysis_prompt(
    supplier: Supplier,
    policies: tuple[PolicyContext, ...]
) -> str:
    policy_context = "\n\n".join(
        (
            f"[Document: {policy.document_id}]"
            f"[Version: {policy.version}]\n"
            f"{policy.content}"
        )
        for policy in policies
    )

    return f"""
        Analyze the supplier using only the supplied data and policy context.

        SUPPLIER:
        {supplier}

        POLICY CONTEXT:
        {policy_context}

        If the policies do not provide sufficient evidence, recommend human review.
        Do not invent policies or supplier information.
        """.strip()