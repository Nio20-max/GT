import NoDataCard from "@/components/NoDataCard";

export default function LineUpPage() {
  return (
    <section>
      <h2 className="mb-6 text-2xl font-bold text-gt-accent">Line Up</h2>
      <NoDataCard
        title="No lineup set"
        message="Pick your starting eleven and formation here."
      />
    </section>
  );
}
