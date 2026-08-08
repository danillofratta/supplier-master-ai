import json

from backend.app.domain.entities.supplier import Supplier


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
) -> str:
    supplier_data = {
        "supplier_id": str(supplier.supplier_id),
        "name": supplier.name,
        "email": supplier.email,
        "phone": supplier.phone,
        "tax_id": supplier.tax_id,
        "status": supplier.status.value,
        "address": {
            "street": supplier.address.street,
            "city": supplier.address.city,
            "state": supplier.address.state,
            "zip_code": supplier.address.zip_code,
            "country": supplier.address.country,
        },
        "available_documents": [],
    }

    return (
        "Analyze the supplier below.\n\n"
        f"Supplier data:\n{json.dumps(supplier_data, ensure_ascii=False)}"
    )