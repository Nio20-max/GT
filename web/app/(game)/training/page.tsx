import NoDataCard from "@/components/NoDataCard";

export default function TrainingPage() {
  return (
    <section>
      <h2 className="mb-6 text-2xl font-bold text-gt-accent">Training</h2>
      <NoDataCard
        title="No training sessions"
        message="Schedule training drills to improve your players."
      />
    </section>
  );
}
