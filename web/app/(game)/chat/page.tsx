import NoDataCard from "@/components/NoDataCard";

export default function ChatPage() {
  return (
    <section>
      <h2 className="mb-6 text-2xl font-bold text-gt-accent">Chat</h2>
      <NoDataCard
        title="No messages"
        message="Chat with other managers in the global chat room."
      />
    </section>
  );
}
