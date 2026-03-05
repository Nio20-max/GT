import NoDataCard from "@/components/NoDataCard";

export default function FinancesPage() {
  return (
    <section>
      <h2 className="mb-6 text-2xl font-bold text-gt-accent">Finances</h2>
      <NoDataCard
        title="No financial data"
        message="Your income, expenses and balance will appear here."
      />
    </section>
  );
}
