import NoDataCard from "@/components/NoDataCard";

export default function EquipmentPage() {
  return (
    <section>
      <h2 className="mb-6 text-2xl font-bold text-gt-accent">Equipment</h2>
      <NoDataCard
        title="No equipment"
        message="Manage kits and gear for your team here."
      />
    </section>
  );
}
