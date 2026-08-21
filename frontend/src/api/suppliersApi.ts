import axios from "axios";
import { httpClient } from "./httpClient";
import type {
  CreateSupplierRequest,
  CreateSupplierResponse,
  StartSupplierOnboardingResponse,
  Supplier,
  SupplierAnalysisResponse,
  SupplierListItem,
  SupplierOnboarding,
  SupplierReviewDecisionRequest,
  SupplierReviewDecisionResponse,
} from "../models/supplier";

interface ListSuppliersResponse {
  items: SupplierListItem[];
}

export async function getSuppliers(): Promise<SupplierListItem[]> {
  const response = await httpClient.get<ListSuppliersResponse>(
    "/v1/suppliers"
  );

  return response.data.items;
}

export async function getSupplier(
  supplierId: string
): Promise<Supplier> {
  const response = await httpClient.get<Supplier>(
    `/v1/suppliers/${supplierId}`
  );

  return response.data;
}

export async function createSupplier(
  request: CreateSupplierRequest
): Promise<CreateSupplierResponse> {
  const response = await httpClient.post<CreateSupplierResponse>(
    "/v1/suppliers",
    request
  );

  return response.data;
}

export async function analyzeSupplier(
  supplierId: string
): Promise<SupplierAnalysisResponse> {
  const response = await httpClient.post<SupplierAnalysisResponse>(
    `/v1/suppliers/${supplierId}/analysis`
  );

  return response.data;
}

export async function getSupplierOnboarding(
  supplierId: string
): Promise<SupplierOnboarding | null> {
  try {
    const response = await httpClient.get<SupplierOnboarding>(
      `/v1/suppliers/${supplierId}/onboarding`
    );

    return response.data;
  } catch (error: unknown) {
    if (
      axios.isAxiosError(error) &&
      error.response?.status === 404
    ) {
      return null;
    }

    throw error;
  }
}

export async function startSupplierOnboarding(
  supplierId: string
): Promise<StartSupplierOnboardingResponse> {
  const response = await httpClient.post<StartSupplierOnboardingResponse>(
    `/v1/suppliers/${supplierId}/onboarding`
  );

  return response.data;
}

export async function decideSupplierReview(
  supplierId: string,
  decision: SupplierReviewDecisionRequest["decision"],
  reason?: string
): Promise<SupplierReviewDecisionResponse> {
  const request: SupplierReviewDecisionRequest = {
    decision,
    reason,
  };

  const response = await httpClient.post<SupplierReviewDecisionResponse>(
    `/v1/suppliers/${supplierId}/onboarding/review-decision`,
    request
  );

  return response.data;
}
