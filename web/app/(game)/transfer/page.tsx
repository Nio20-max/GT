import NoDataCard from "@/components/NoDataCard";

export default function TransferPage() {
  return (
    <section>
      <h2 className="mb-6 text-2xl font-bold text-gt-accent">Transfer Market</h2>
      <NoDataCard
        title="No listings"
        message="Browse and bid on players available for transfer."
      />
    </section>
  );
}
