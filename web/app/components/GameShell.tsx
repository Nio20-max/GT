"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { NAV_ITEMS } from "../lib/navigation";

export default function GameShell({ title, children }: { title: string; children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <main className="app-shell">
      <aside className="left-menu">
        <h1>Goal Tactics</h1>
        <nav>
          {NAV_ITEMS.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={`nav-link ${pathname === item.href ? "is-active" : ""}`.trim()}
            >
              {item.label}
            </Link>
          ))}
        </nav>
      </aside>
      <section className="content">
        <header className="economy-bar">
          <span>Money: 5,000,000</span>
          <span>Stars: 20,000</span>
          <span>Medipacks: 0</span>
        </header>
        <article className="panel">
          <h2>{title}</h2>
          {children}
        </article>
      </section>
    </main>
  );
}
