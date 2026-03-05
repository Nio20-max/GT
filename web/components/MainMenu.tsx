"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

interface MenuItem {
  label: string;
  href: string;
}

interface MenuSection {
  title: string;
  items: MenuItem[];
}

const sections: MenuSection[] = [
  {
    title: "Team",
    items: [
      { label: "Club", href: "/club" },
      { label: "Finances", href: "/finances" },
      { label: "Stadium", href: "/stadium" },
      { label: "Squad", href: "/squad" },
      { label: "Equipment", href: "/equipment" },
      { label: "Line Up", href: "/lineup" },
      { label: "Training", href: "/training" },
      { label: "Scouting", href: "/scouting" },
    ],
  },
  {
    title: "Competitions",
    items: [
      { label: "Transfer Market", href: "/transfer" },
      { label: "League", href: "/league" },
      { label: "GT Ladder", href: "/ladder" },
    ],
  },
  {
    title: "Social",
    items: [
      { label: "Friends", href: "/friends" },
      { label: "Live", href: "/live" },
      { label: "Chat", href: "/chat" },
    ],
  },
  {
    title: "Other",
    items: [{ label: "Shop", href: "/shop" }],
  },
];

export default function MainMenu() {
  const pathname = usePathname();

  return (
    <nav className="flex h-full w-56 flex-col overflow-y-auto bg-gt-green py-4 text-sm">
      {sections.map((section) => (
        <div key={section.title} className="mb-2">
          <h3 className="px-4 py-1 text-xs font-bold uppercase tracking-wider text-gt-section">
            {section.title}
          </h3>
          {section.items.map((item) => {
            const active = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`block px-4 py-2 transition-colors ${
                  active
                    ? "bg-gt-accent text-gt-bg font-semibold"
                    : "text-white hover:bg-gt-accent/20"
                }`}
              >
                {item.label}
              </Link>
            );
          })}
        </div>
      ))}
    </nav>
  );
}
