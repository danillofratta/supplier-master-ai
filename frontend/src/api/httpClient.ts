import axios from "axios";

export const httpClient = axios.create({
  baseURL:
    import.meta.env.VITE_API_URL ??
    "http://localhost:8000/api",
  timeout: 15000,
  headers: {
    "Content-Type": "application/json",
  },
});

httpClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const correlationId =
      error?.response?.headers?.["x-correlation-id"];

    if (correlationId) {
      error.correlationId = correlationId;
    }

    return Promise.reject(error);
  }
);
