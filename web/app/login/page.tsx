"use client";

import { FormEvent, useState } from "react";

import GameShell from "../components/GameShell";
import { setStoredToken } from "../lib/authToken";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "";

export default function LoginPage() {
  const [token, setToken] = useState("");
  const [message, setMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsLoading(true);
    setMessage("");
    const form = new FormData(event.currentTarget);
    const username = String(form.get("username") ?? "");
    const password = String(form.get("password") ?? "");

    try {
      const response = await fetch(`${API_BASE}/api/v1/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });
      const payload = await response.json();
      if (payload.ok) {
        const nextToken = payload.data.token as string;
        setToken(nextToken);
        setStoredToken(nextToken);

        const profileResp = await fetch(`${API_BASE}/api/v1/me/profile`, {
          headers: { Authorization: `Bearer ${nextToken}` },
        });
        const profilePayload = await profileResp.json();
        if (profilePayload.ok && profilePayload.data.authenticated) {
          setMessage(`Logged in as ${profilePayload.data.user.username}`);
        } else {
          setMessage("Login succeeded but profile lookup failed");
        }
      } else {
        setMessage(payload.error?.message ?? "Login failed");
      }
    } catch {
      setMessage("Network error while logging in");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <GameShell title="Login">
      <form className="auth-form" onSubmit={onSubmit}>
        <label>
          Username
          <input name="username" required />
        </label>
        <label>
          Password
          <input name="password" type="password" required minLength={8} />
        </label>
        <button type="submit" disabled={isLoading}>
          {isLoading ? "Logging in..." : "Login"}
        </button>
      </form>
      {message ? <p className="status">{message}</p> : null}
      {token ? <p className="status token">Token: {token.slice(0, 24)}...</p> : null}
    </GameShell>
  );
}
