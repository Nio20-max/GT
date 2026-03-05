import NoDataCard from "@/components/NoDataCard";

export default function StadiumPage() {
  return (
    <section>
      <h2 className="mb-6 text-2xl font-bold text-gt-accent">Stadium</h2>
      <NoDataCard
        title="No stadium data"
        message="Upgrade and manage your stadium here."
      />
    </section>
  );
}
