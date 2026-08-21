import axios from "axios";

interface ApiErrorBody {
  detail?: string;
  message?: string;
  code?: string;
}

export function getApiErrorMessage(
  error: unknown,
  fallback: string
): string {
  if (!axios.isAxiosError<ApiErrorBody>(error)) {
    return fallback;
  }

  const body = error.response?.data;

  if (typeof body?.detail === "string" && body.detail.trim()) {
    return body.detail;
  }

  if (typeof body?.message === "string" && body.message.trim()) {
    return body.message;
  }

  if (error.code === "ECONNABORTED") {
    return "The request timed out. Check the API Gateway and downstream services.";
  }

  if (!error.response) {
    return "Unable to reach the API Gateway.";
  }

  return fallback;
}
