import NoDataCard from "@/components/NoDataCard";

export default function LeaguePage() {
  return (
    <section>
      <h2 className="mb-6 text-2xl font-bold text-gt-accent">League</h2>
      <NoDataCard
        title="No league data"
        message="Standings, fixtures and results will appear here."
      />
    </section>
  );
}
