// mycelium/frontend/src/lib/api.ts
// Typed API client for MYCELIUM backend

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const API_V1 = `${API_BASE}/api/v1`;

class ApiError extends Error {
  constructor(
    public status: number,
    public detail: string
  ) {
    super(`API ${status}: ${detail}`);
  }
}

async function apiFetch<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const response = await fetch(`${API_V1}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({ detail: "Unknown error" }));
    throw new ApiError(response.status, body.detail ?? "Unknown error");
  }

  return response.json() as Promise<T>;
}

// ─── GENOME API ───────────────────────────────────────────────────────────────

export interface GenomeListResponse {
  genomes: unknown[];
  total: number;
  skip: number;
  limit: number;
}

export interface GenomeLineageResponse {
  genome_id: string;
  ancestors: unknown[];
  descendants: unknown[];
}

export const genomesApi = {
  list: (params?: { skip?: number; limit?: number; status?: string }) => {
    const qs = new URLSearchParams(
      Object.entries(params ?? {}).filter(([, v]) => v !== undefined) as [string, string][]
    ).toString();
    return apiFetch<GenomeListResponse>(`/genomes${qs ? `?${qs}` : ""}`);
  },

  get: (id: string) => apiFetch<unknown>(`/genomes/${id}`),

  lineage: (id: string, depth = 10) =>
    apiFetch<GenomeLineageResponse>(`/genomes/${id}/lineage?depth=${depth}`),

  extinct: (id: string) =>
    apiFetch<{ message: string }>(`/genomes/${id}`, { method: "DELETE" }),
};

// ─── HEALTH API ───────────────────────────────────────────────────────────────

export interface HealthResponse {
  status: string;
  service: string;
  version: string;
  environment: string;
  timestamp: number;
}

export const healthApi = {
  check: () => apiFetch<HealthResponse>("/health/"),
  ready: () => apiFetch<{ status: string; checks: Record<string, { status: string }> }>("/health/ready"),
};

export { ApiError };
