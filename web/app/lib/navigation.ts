export type NavItem = {
  href: string;
  label: string;
};

export type SectionData = {
  title: string;
  summary: string;
  bullets: string[];
};

export const NAV_ITEMS: NavItem[] = [
  { href: "/", label: "Dashboard" },
  { href: "/club", label: "Club" },
  { href: "/squad", label: "Squad" },
  { href: "/lineup", label: "Lineup" },
  { href: "/training", label: "Training" },
  { href: "/market", label: "Market" },
  { href: "/league", label: "League" },
  { href: "/register", label: "Register" },
  { href: "/login", label: "Login" },
];

export const SECTION_DATA: Record<string, SectionData> = {
  club: {
    title: "Club",
    summary: "Manage identity, fans, sponsors, and long-term growth.",
    bullets: [
      "Track club profile and development milestones.",
      "Review sponsor offers and historical accomplishments.",
      "Monitor fans and member health as your club scales.",
    ],
  },
  squad: {
    title: "Squad",
    summary: "Inspect players, compare strengths, and plan upgrades.",
    bullets: [
      "View player cards and current role distribution.",
      "Prepare progression paths for key starters and prospects.",
      "Coordinate with training and market plans.",
    ],
  },
  lineup: {
    title: "Lineup",
    summary: "Set formations and starting decisions for upcoming fixtures.",
    bullets: [
      "Switch between current and upcoming lineups.",
      "Keep lock windows in mind before match kickoff.",
      "Align tactics with opponent strengths.",
    ],
  },
  training: {
    title: "Training",
    summary: "Run team and individual training with deterministic progression.",
    bullets: [
      "Preview expected gains before applying plans.",
      "Balance fatigue and growth pace over the season.",
      "Use camps and tactic drills for focused improvements.",
    ],
  },
  market: {
    title: "Transfer Market",
    summary: "Scout and trade to keep your roster competitive.",
    bullets: [
      "Browse auctions, bids, and favorites in one place.",
      "Time bids around daily schedule windows.",
      "Use injections and finances data to budget safely.",
    ],
  },
  league: {
    title: "League",
    summary: "Follow season progression, fixtures, and table outcomes.",
    bullets: [
      "Check table movement and top scorers.",
      "Review fixture/results timeline for tactical adjustments.",
      "Coordinate cup and UCL overlaps with roster depth.",
    ],
  },
};
