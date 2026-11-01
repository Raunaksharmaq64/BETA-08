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

// Client-side high-speed in-memory cache for instant tab transitions
const clientApiCache = new Map<string, { timestamp: number; payload: any }>();
const CLIENT_CACHE_TTL_MS = 60000; // 60s fast in-memory cache
const inFlightRequests = new Map<string, Promise<any>>();

export async function apiClient<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> {
  const method = (options.method || "GET").toUpperCase();

  // Support both full paths and relative paths
  let url: string;
  if (endpoint.startsWith("http")) {
    url = endpoint;
  } else if (endpoint.startsWith("/api/v1")) {
    const root = API_BASE_URL.replace("/api/v1", "");
    url = `${root}${endpoint}`;
  } else {
    url = `${API_BASE_URL}${endpoint.startsWith("/") ? endpoint : `/${endpoint}`}`;
  }

  // Clear cache on any write/mutation operation
  if (method !== "GET") {
    clientApiCache.clear();
  } else {
    const cached = clientApiCache.get(url);
    if (cached && Date.now() - cached.timestamp < CLIENT_CACHE_TTL_MS) {
      return cached.payload as ApiResponse<T>;
    }
    const ongoing = inFlightRequests.get(url);
    if (ongoing) {
      return ongoing as Promise<ApiResponse<T>>;
    }
  }

  const executeFetch = async (): Promise<ApiResponse<T>> => {
    const isFormData = typeof FormData !== "undefined" && options.body instanceof FormData;

    const headers: HeadersInit = {
      ...(isFormData ? {} : { "Content-Type": "application/json" }),
      ...(options.headers || {}),
    };

    const response = await fetch(url, {
      ...options,
      headers,
      credentials: "include", // Enables HttpOnly cookie authentication
    });

    let responseData: any;
    const contentType = response.headers.get("content-type") || "";
    if (contentType.includes("application/json")) {
      responseData = await response.json();
    } else {
      const text = await response.text();
      responseData = { success: response.ok, data: text };
    }

    if (!response.ok || (typeof responseData === "object" && responseData !== null && responseData.success === false)) {
      const errorPayload: ApiError = responseData?.error || {
        code: "UNKNOWN_ERROR",
        message: responseData?.detail || responseData?.message || "An unexpected error occurred.",
        request_id: response.headers.get("x-request-id") || "",
        service: "frontend_gateway",
        retryable: false,
      };
      throw errorPayload;
    }

    // Handle direct return models
    let finalReturn: any;
    if (responseData && typeof responseData === "object" && !("success" in responseData)) {
      finalReturn = {
        success: true,
        data: responseData as T,
        meta: {
          request_id: response.headers.get("x-request-id") || "",
          timestamp: new Date().toISOString(),
          service: "core_career_engine",
        },
      };
    } else {
      finalReturn = responseData;
    }

    if (method === "GET") {
      clientApiCache.set(url, { timestamp: Date.now(), payload: finalReturn });
    }

    return finalReturn;
  };

  if (method === "GET") {
    const reqPromise = executeFetch();
    inFlightRequests.set(url, reqPromise);
    try {
      return await reqPromise;
    } finally {
      inFlightRequests.delete(url);
    }
  }

  return executeFetch();
}

// Convenience methods
apiClient.clearCache = function () {
  clientApiCache.clear();
};

apiClient.get = function <T>(endpoint: string, options: RequestInit = {}) {
  return apiClient<T>(endpoint, { ...options, method: "GET" });
};

apiClient.post = function <T>(endpoint: string, body?: any, options: RequestInit = {}) {
  return apiClient<T>(endpoint, {
    ...options,
    method: "POST",
    body: body ? JSON.stringify(body) : undefined,
  });
};

apiClient.postForm = function <T>(endpoint: string, formData: FormData, options: RequestInit = {}) {
  return apiClient<T>(endpoint, {
    ...options,
    method: "POST",
    body: formData,
  });
};

apiClient.put = function <T>(endpoint: string, body?: any, options: RequestInit = {}) {
  return apiClient<T>(endpoint, {
    ...options,
    method: "PUT",
    body: body ? JSON.stringify(body) : undefined,
  });
};

apiClient.patch = function <T>(endpoint: string, body?: any, options: RequestInit = {}) {
  return apiClient<T>(endpoint, {
    ...options,
    method: "PATCH",
    body: body ? JSON.stringify(body) : undefined,
  });
};

apiClient.delete = function <T>(endpoint: string, options: RequestInit = {}) {
  return apiClient<T>(endpoint, { ...options, method: "DELETE" });
};

