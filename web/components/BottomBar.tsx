"use client";

export default function BottomBar() {
  return (
    <footer className="flex h-10 items-center justify-around border-t border-gt-accent/30 bg-gt-green px-4 text-xs font-medium text-white">
      <span className="flex items-center gap-1">
        <span className="text-base">💊</span>
        <span>0</span>
      </span>
      <span className="flex items-center gap-1">
        <span className="text-base">⭐</span>
        <span>0</span>
      </span>
      <span className="flex items-center gap-1">
        <span className="text-base">💰</span>
        <span>$0</span>
      </span>
    </footer>
  );
}
