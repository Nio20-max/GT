import NoDataCard from "@/components/NoDataCard";

export default function ScoutingPage() {
  return (
    <section>
      <h2 className="mb-6 text-2xl font-bold text-gt-accent">Scouting</h2>
      <NoDataCard
        title="No scouting reports"
        message="Send scouts to discover new talent around the world."
      />
    </section>
  );
}
