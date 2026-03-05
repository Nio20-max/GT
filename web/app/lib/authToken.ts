const TOKEN_KEY = "gt_auth_token";

function getCookieToken(): string {
  if (typeof document === "undefined") {
    return "";
  }
  const parts = document.cookie.split(";").map((part) => part.trim());
  const match = parts.find((part) => part.startsWith(`${TOKEN_KEY}=`));
  if (!match) {
    return "";
  }
  return decodeURIComponent(match.slice(TOKEN_KEY.length + 1));
}

export function getStoredToken(): string {
  if (typeof window === "undefined") {
    return "";
  }
  return window.localStorage.getItem(TOKEN_KEY) ?? getCookieToken();
}

export function setStoredToken(token: string): void {
  if (typeof window === "undefined") {
    return;
  }
  window.localStorage.setItem(TOKEN_KEY, token);
  document.cookie = `${TOKEN_KEY}=${encodeURIComponent(token)}; Path=/; Max-Age=2592000; SameSite=Lax`;
}

export function clearStoredToken(): void {
  if (typeof window === "undefined") {
    return;
  }
  window.localStorage.removeItem(TOKEN_KEY);
  document.cookie = `${TOKEN_KEY}=; Path=/; Max-Age=0; SameSite=Lax`;
}
