import Link from "next/link";

import GameShell from "./components/GameShell";
import { SECTION_DATA } from "./lib/navigation";

export default function HomePage() {
  const featureCards = Object.entries(SECTION_DATA);

  return (
    <GameShell title="Dashboard">
      <p className="intro-text">Everything in the left menu is now mapped to a real route with usable page content.</p>
      <div className="card-grid">
        {featureCards.map(([slug, section]) => (
          <section key={slug} className="feature-card">
            <h3>{section.title}</h3>
            <p>{section.summary}</p>
            <Link href={`/${slug}`} className="inline-link">
              Open {section.title}
            </Link>
          </section>
        ))}
      </div>
      <div className="auth-cta">
        <Link href="/register" className="inline-link">
          Create Account
        </Link>
        <Link href="/login" className="inline-link">
          Login
        </Link>
      </div>
    </GameShell>
  );
}
