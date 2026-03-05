import Link from "next/link";

import GameShell from "./components/GameShell";

export default function NotFound() {
  return (
    <GameShell title="Page Not Found">
      <p className="intro-text">That route does not exist in the current web client.</p>
      <div className="auth-cta">
        <Link href="/" className="inline-link">
          Back To Dashboard
        </Link>
        <Link href="/league" className="inline-link">
          Open League
        </Link>
      </div>
    </GameShell>
  );
}
