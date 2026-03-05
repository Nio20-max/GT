import NoDataCard from "@/components/NoDataCard";

export default function LivePage() {
  return (
    <section>
      <h2 className="mb-6 text-2xl font-bold text-gt-accent">Live</h2>
      <NoDataCard
        title="No live matches"
        message="Watch live matches and follow the action in real time."
      />
    </section>
  );
}
