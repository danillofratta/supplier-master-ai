import { httpClient } from "./httpClient";
import type { IngestPolicyRequest, IngestPolicyResponse } from "../models/supplier";

export async function ingestPolicy(request: IngestPolicyRequest): Promise<IngestPolicyResponse> {
  const response = await httpClient.post<IngestPolicyResponse>("/v1/policies/ingest", request);
  return response.data;
}
