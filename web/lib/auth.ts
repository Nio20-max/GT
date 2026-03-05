/* JWT token helpers for Goal Tactics */

const TOKEN_KEY = "gt_token";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}

export function isAuthenticated(): boolean {
  return getToken() !== null;
}

/** Decode the payload of a JWT (no verification – server is the authority). */
export function decodePayload<T = Record<string, unknown>>(
  token: string,
): T | null {
  try {
    const base64 = token.split(".")[1];
    const json = atob(base64);
    return JSON.parse(json) as T;
  } catch {
    return null;
  }
}
