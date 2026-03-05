import NoDataCard from "@/components/NoDataCard";

export default function FriendsPage() {
  return (
    <section>
      <h2 className="mb-6 text-2xl font-bold text-gt-accent">Friends</h2>
      <NoDataCard
        title="No friends yet"
        message="Add friends and challenge them to matches."
      />
    </section>
  );
}
