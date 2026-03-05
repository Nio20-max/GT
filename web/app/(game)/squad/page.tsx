import NoDataCard from "@/components/NoDataCard";

export default function SquadPage() {
  return (
    <section>
      <h2 className="mb-6 text-2xl font-bold text-gt-accent">Squad</h2>
      <NoDataCard
        title="No players yet"
        message="Your squad roster will be displayed here."
      />
    </section>
  );
}
