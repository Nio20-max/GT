import NoDataCard from "@/components/NoDataCard";

export default function ClubPage() {
  return (
    <section>
      <h2 className="mb-6 text-2xl font-bold text-gt-accent">Club</h2>
      <NoDataCard
        title="No club data"
        message="Your club overview will appear here once you start playing."
      />
    </section>
  );
}
