/**
 * RIGHT FIT — Frontend Central API Client
 * Version: 1.0.0
 * Phase: 3 — Identity, Candidate Profile & Privacy Foundation
 */

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  meta: {
    request_id: string;
    timestamp: string;
    service: string;
  };
}

export interface ApiError {
  code: string;
  message: string;
  details?: Array<{ field?: string; issue: string; rejected_value?: any }>;
  request_id: string;
  service: string;
  retryable: boolean;
}

export async function apiClient<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> {
  const url = `${API_BASE_URL}${endpoint.startsWith("/") ? endpoint : `/${endpoint}`}`;

  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };

  const response = await fetch(url, {
    ...options,
    headers,
    credentials: "include", // Enables HttpOnly cookie authentication
  });

  const responseData = await response.json();

  if (!response.ok || !responseData.success) {
    const errorPayload: ApiError = responseData.error || {
      code: "UNKNOWN_ERROR",
      message: responseData.detail || "An unexpected error occurred.",
      request_id: response.headers.get("x-request-id") || "",
      service: "frontend_gateway",
      retryable: false,
    };
    throw errorPayload;
  }

  return responseData;
}
