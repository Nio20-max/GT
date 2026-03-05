export type ApiEnvelope<T> = {
  ok: boolean;
  data: T;
  error?: { code: string; message: string };
  traceId?: string;
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "";

export async function apiGet<T>(path: string, token?: string): Promise<ApiEnvelope<T>> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: token ? { Authorization: `Bearer ${token}` } : undefined,
  });
  return (await response.json()) as ApiEnvelope<T>;
}

export async function apiPost<T>(
  path: string,
  body: unknown,
  token?: string,
  extraHeaders?: Record<string, string>
): Promise<ApiEnvelope<T>> {
  const headers: Record<string, string> = { "Content-Type": "application/json", ...(extraHeaders ?? {}) };
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  const response = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers,
    body: JSON.stringify(body),
  });
  return (await response.json()) as ApiEnvelope<T>;
}

export async function apiPut<T>(path: string, body: unknown, token?: string): Promise<ApiEnvelope<T>> {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  const response = await fetch(`${API_BASE}${path}`, {
    method: "PUT",
    headers,
    body: JSON.stringify(body),
  });
  return (await response.json()) as ApiEnvelope<T>;
}
