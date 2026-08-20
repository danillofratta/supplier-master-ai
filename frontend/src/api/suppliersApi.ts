import { httpClient } from "./httpClient";
import type {
  CreateSupplierRequest,
  CreateSupplierResponse,
  Supplier,
  SupplierAnalysisResponse,
  SupplierListItem,
  SupplierOnboarding,
} from "../models/supplier";

interface ListSuppliersResponse {
  items: SupplierListItem[];
}

export async function getSuppliers(): Promise<
  SupplierListItem[]
> {
  const response =
    await httpClient.get<ListSuppliersResponse>(
      "/v1/suppliers"
    );

  return response.data.items;
}

export async function getSupplier(
  supplierId: string
): Promise<Supplier> {
  const response =
    await httpClient.get<Supplier>(
      `/v1/suppliers/${supplierId}`
    );

  return response.data;
}

export async function createSupplier(
  request: CreateSupplierRequest
): Promise<CreateSupplierResponse> {
  const response =
    await httpClient.post<CreateSupplierResponse>(
      "/v1/suppliers",
      request
    );

  return response.data;
}

export async function analyzeSupplier(
  supplierId: string
): Promise<SupplierAnalysisResponse> {
  
  const response =
    await httpClient.post<SupplierAnalysisResponse>(
      `/v1/suppliers/${supplierId}/analysis`
    );

  return response.data;
}

export async function getSupplierOnboarding(
  supplierId: string
): Promise<SupplierOnboarding | null> {
  try {
    const response =
      await httpClient.get<SupplierOnboarding>(
        `/v1/suppliers/${supplierId}/onboarding`
      );

    return response.data;
  } catch (error: any) {
    if (error?.response?.status === 404) {
      return null;
    }

    throw error;
  }
}
