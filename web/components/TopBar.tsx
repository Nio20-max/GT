"use client";

interface TopBarProps {
  title?: string;
}

export default function TopBar({ title = "Goal Tactics" }: TopBarProps) {
  return (
    <header className="flex h-12 items-center justify-between bg-gt-green px-4 shadow-md">
      <h1 className="text-lg font-bold text-gt-accent">{title}</h1>
      <div className="flex items-center gap-3">
        <span className="text-xs text-white/70">v0.1.0</span>
      </div>
    </header>
  );
}
