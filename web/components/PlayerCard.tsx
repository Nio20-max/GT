import type { Player } from "@/lib/types";

interface PlayerCardProps {
  player: Player;
}

export default function PlayerCard({ player }: PlayerCardProps) {
  return (
    <div className="flex items-center gap-4 rounded-lg bg-gt-green/60 p-4">
      {/* Avatar placeholder */}
      <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-full bg-gt-accent text-xl font-bold text-gt-bg">
        {player.position}
      </div>

      <div className="flex flex-col">
        <span className="font-semibold text-white">{player.name}</span>
        <span className="text-xs text-white/70">
          Age {player.age} · {player.position}
        </span>
      </div>

      <div className="ml-auto text-right">
        <span className="text-2xl font-bold text-gt-highlight">
          {player.rating}
        </span>
        <span className="block text-[10px] uppercase text-white/50">
          Overall
        </span>
      </div>
    </div>
  );
}
