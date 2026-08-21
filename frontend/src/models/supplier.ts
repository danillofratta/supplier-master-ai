export interface SupplierListItem {
  supplier_id: string;
  name: string;
  email: string;
  tax_id: string;
  status: string;
}

export interface Supplier {
  supplier_id: string;
  name: string;
  email: string;
  phone: string;
  tax_id: string;
  status: string;
  street: string;
  city: string;
  state: string;
  zip_code: string;
  country: string;
}

export interface SupplierOnboarding {
  workflow_id: string;
  correlation_id: string;
  supplier_id: string;
  status: string;
  service_now_ticket_id: string | null;
  sap_business_partner_id: string | null;
  rejection_reason: string | null;
  failure_reason: string | null;
  created_at: string;
  updated_at: string;
}

export interface CreateSupplierRequest {
  name: string;
  email: string;
  phone: string;
  tax_id: string;
  address: {
    street: string;
    city: string;
    state: string;
    zip_code: string;
    country: string;
  };
}

export interface CreateSupplierResponse {
  supplier_id: string;
  name: string;
  email: string;
  phone: string;
  tax_id: string;
  status: string;
  address: CreateSupplierRequest["address"];
}

export interface SupplierAnalysisResponse {
  risk_level: string;
  recommended_action: string;
  summary: string;
  confidence: number;
  missing_documents: string[];
  policy_violations: string[];
  retrieved_policy_ids: string[];
}

export interface StartSupplierOnboardingResponse {
  onboarding_workflow_id: string;
  supplier_id: string;
  status: string;
}

export interface SupplierReviewDecisionRequest {
  decision: "approve" | "reject";
  reason?: string;
}

export interface IngestPolicyRequest {
  document_id: string;
  title: string;
  content: string;
  policy_type: string;
  version: string;
  effective_date: string;
}

export interface IngestPolicyResponse {
  document_id: string;
  chunks_indexed: number;
  embedding_dimensions: number;
}

export interface SupplierReviewDecisionResponse {
  workflow_id: string;
  supplier_id: string;
  status: string;
}
