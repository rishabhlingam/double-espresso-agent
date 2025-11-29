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

  // If no chat selected
  if (!chat) {
    return (
      <div className="flex-1 flex items-center justify-center bg-gray-900 text-white">
        <button
          className="px-6 py-3 bg-blue-600 rounded-lg text-lg"
          onClick={onStartNewChat}
        >
          Start New Chat
        </button>
      </div>
    );
  }

  const messages = chat.messages || [];

  return (
    <div className="flex flex-col flex-1 bg-gray-900 text-white">

      {/* Messages list */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-2">
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
        autoComplete="off"           // <--- disables unwanted browser suggestions
        onSubmit={(e) => {
          e.preventDefault();
          const text = e.target.msg.value;
          if (text.trim()) onSend(text);
          e.target.reset();
        }}
        className="p-4 border-t border-gray-800 flex gap-3 bg-gray-900"
      >
        <input
          name="msg"
          autoComplete="off"         // <--- double safety
          className="flex-1 p-3 rounded-xl bg-gray-800 text-white
                     focus:ring-2 focus:ring-blue-600 outline-none"
          placeholder="Message CoffeeLM…"
        />

        <button className="px-6 py-3 bg-blue-600 rounded-xl hover:bg-blue-700 transition">
          Send
        </button>
      </form>

    </div>
  );
}
