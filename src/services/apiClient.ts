/**
 * RightFit Unified API Client
 *
 * Defaults to modular mock data out of the box.
 * To connect to your premade backend, create a .env.local file:
 *   NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
 *   NEXT_PUBLIC_USE_MOCK_DATA=false
 */

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

export const IS_MOCK_MODE =
  process.env.NEXT_PUBLIC_USE_MOCK_DATA !== 'false';

export interface RequestOptions extends RequestInit {
  params?: Record<string, string | number | boolean | undefined>;
}

export class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private buildUrl(
    endpoint: string,
    params?: Record<string, string | number | boolean | undefined>
  ): string {
    const url = new URL(endpoint, this.baseUrl);
    if (params) {
      Object.entries(params).forEach(([key, val]) => {
        if (val !== undefined) {
          url.searchParams.append(key, String(val));
        }
      });
    }
    return url.toString();
  }

  async get<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
    const url = this.buildUrl(endpoint, options.params);
    const res = await fetch(url, {
      ...options,
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!res.ok) {
      throw new Error(`API Error [GET ${endpoint}]: ${res.status} ${res.statusText}`);
    }
    return res.json() as Promise<T>;
  }

  async post<T>(
    endpoint: string,
    body: unknown,
    options: RequestOptions = {}
  ): Promise<T> {
    const url = this.buildUrl(endpoint, options.params);
    const res = await fetch(url, {
      ...options,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      body: JSON.stringify(body),
    });

    if (!res.ok) {
      throw new Error(`API Error [POST ${endpoint}]: ${res.status} ${res.statusText}`);
    }
    return res.json() as Promise<T>;
  }

  async patch<T>(
    endpoint: string,
    body: unknown,
    options: RequestOptions = {}
  ): Promise<T> {
    const url = this.buildUrl(endpoint, options.params);
    const res = await fetch(url, {
      ...options,
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      body: JSON.stringify(body),
    });

    if (!res.ok) {
      throw new Error(`API Error [PATCH ${endpoint}]: ${res.status} ${res.statusText}`);
    }
    return res.json() as Promise<T>;
  }
}

export const apiClient = new ApiClient();

// Helper to simulate network latency in mock mode
export const delay = (ms: number = 100): Promise<void> =>
  new Promise((resolve) => setTimeout(resolve, ms));

