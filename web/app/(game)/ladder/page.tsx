import NoDataCard from "@/components/NoDataCard";

export default function LadderPage() {
  return (
    <section>
      <h2 className="mb-6 text-2xl font-bold text-gt-accent">GT Ladder</h2>
      <NoDataCard
        title="No ladder data"
        message="Climb the GT Ladder by winning competitive matches."
      />
    </section>
  );
}
