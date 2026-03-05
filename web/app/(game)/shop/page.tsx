import NoDataCard from "@/components/NoDataCard";

export default function ShopPage() {
  return (
    <section>
      <h2 className="mb-6 text-2xl font-bold text-gt-accent">Shop</h2>
      <NoDataCard
        title="Shop coming soon"
        message="Purchase medipacks, stars and other items here."
      />
    </section>
  );
}
