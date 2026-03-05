import { notFound } from "next/navigation";
import Link from "next/link";

import GameShell from "../components/GameShell";
import LiveSectionData from "../components/section/LiveSectionData";
import SectionActions from "../components/section/SectionActions";
import { SECTION_DATA } from "../lib/navigation";

export default async function SectionPage({
  params,
}: {
  params: Promise<{ section: string }>;
}) {
  const { section: sectionKey } = await params;
  const section = SECTION_DATA[sectionKey];
  if (!section) {
    notFound();
  }

  return (
    <GameShell title={section.title}>
      <p className="intro-text">{section.summary}</p>
      <LiveSectionData sectionKey={sectionKey} />
      <SectionActions sectionKey={sectionKey} />
      <ul className="bullet-list">
        {section.bullets.map((bullet) => (
          <li key={bullet}>{bullet}</li>
        ))}
      </ul>
      <div className="auth-cta">
        <Link href="/" className="inline-link">
          Dashboard
        </Link>
        <Link href="/login" className="inline-link">
          Open Login
        </Link>
      </div>
    </GameShell>
  );
}
