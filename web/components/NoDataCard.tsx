interface NoDataCardProps {
  title?: string;
  message?: string;
  actionLabel?: string;
  onAction?: () => void;
}

export default function NoDataCard({
  title = "Nothing here yet",
  message = "Check back later or take an action to get started.",
  actionLabel,
  onAction,
}: NoDataCardProps) {
  return (
    <div className="mx-auto flex max-w-sm flex-col items-center gap-4 rounded-xl bg-gt-green/60 p-8 text-center">
      {/* Placeholder character */}
      <div className="flex h-24 w-24 items-center justify-center rounded-full bg-gt-accent/20 text-5xl">
        ⚽
      </div>

      <h2 className="text-xl font-bold text-gt-highlight">{title}</h2>
      <p className="text-sm text-white/80">{message}</p>

      {actionLabel && onAction && (
        <button
          type="button"
          onClick={onAction}
          className="rounded-lg bg-gt-accent px-6 py-2 text-sm font-semibold text-gt-bg transition hover:brightness-110"
        >
          {actionLabel}
        </button>
      )}
    </div>
  );
}
