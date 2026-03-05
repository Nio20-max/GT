"use client";

import { FormEvent, useState } from "react";

import GameShell from "../components/GameShell";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "";

export default function RegisterPage() {
  const [message, setMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsLoading(true);
    setMessage("");
    const form = new FormData(event.currentTarget);
    const username = String(form.get("username") ?? "");
    const email = String(form.get("email") ?? "");
    const password = String(form.get("password") ?? "");

    try {
      const response = await fetch(`${API_BASE}/api/v1/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, email, password }),
      });
      const payload = await response.json();
      if (payload.ok) {
        const avg = payload.data.starterSquad?.averageStrength;
        const avgText = typeof avg === "number" ? ` | starter squad avg: ${avg}` : "";
        setMessage(`Account created for ${payload.data.user.username}${avgText}`);
        event.currentTarget.reset();
      } else {
        setMessage(payload.error?.message ?? "Registration failed");
      }
    } catch {
      setMessage("Network error while registering");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <GameShell title="Register">
      <form className="auth-form" onSubmit={onSubmit}>
        <label>
          Username
          <input name="username" required minLength={3} />
        </label>
        <label>
          Email
          <input name="email" type="email" required />
        </label>
        <label>
          Password
          <input name="password" type="password" required minLength={8} />
        </label>
        <button type="submit" disabled={isLoading}>
          {isLoading ? "Creating..." : "Create Account"}
        </button>
      </form>
      {message ? <p className="status">{message}</p> : null}
    </GameShell>
  );
}
