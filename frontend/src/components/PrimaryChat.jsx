import MessageBubble from "./MessageBubble";
import { useEffect, useRef } from "react";

export default function PrimaryChat({
  chat,
  onSend,
  onDrillDown,
  onStartNewChat,
}) {
  const bottomRef = useRef(null);

  // Auto scroll to bottom whenever messages update
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chat?.messages]);

  // If no chat selected → Welcome screen
  if (!chat) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center bg-espresso text-cream px-6 text-center">
        <h1 className="text-3xl font-bold mb-4">Welcome to Double Espresso Agent</h1>
        <p className="text-latte text-lg mb-6">
          Your intelligent multi-agent assistant. Start a new chat to begin.
        </p>
        <button
          className="px-6 py-3 bg-caramel text-espresso rounded-lg text-lg hover:bg-gold transition"
          onClick={onStartNewChat}
        >
          Start New Chat
        </button>
      </div>
    );
  }

  const messages = chat.messages || [];

  return (
    <div className="flex flex-col flex-1 bg-espresso text-cream">

      {/* Messages list */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-2 bg-espresso">
        {messages.map((m) => (
          <MessageBubble
            key={m.id}
            id={m.id}
            role={m.role}
            content={m.content}
            isThinking={m.isThinking === true}
            isSecondary={false}
            onDrillDown={() => onDrillDown(m.id)}
          />
        ))}
        <div ref={bottomRef} />
      </div>

      {/* Input box */}
      <form
        autoComplete="off"
        onSubmit={(e) => {
          e.preventDefault();
          const text = e.target.msg.value;
          if (text.trim()) onSend(text);
          e.target.reset();
        }}
        className="p-4 border-t border-mocha flex gap-3 bg-mocha"
      >
        <input
          name="msg"
          autoComplete="off"
          className="flex-1 p-3 rounded-xl bg-foam text-cream placeholder-latte
                     focus:ring-2 focus:ring-caramel outline-none"
          placeholder="Brew your message…"
        />

        <button className="px-6 py-3 bg-caramel text-espresso rounded-xl hover:bg-gold transition">
          Send
        </button>
      </form>

    </div>
  );
}
