import { useEffect, useRef, useState } from "react";
import MessageBubble from "./MessageBubble";

export default function SecondaryChatOverlay({ chat, onSend, onClose }) {
  const bottomRef = useRef(null);
  const [closing, setClosing] = useState(false);

  // Auto-scroll on new messages
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chat?.messages]);

  // ESC closes overlay
  useEffect(() => {
    const handler = (e) => {
      if (e.key === "Escape") handleClose();
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, []);

  const handleClose = () => {
    setClosing(true);
    setTimeout(onClose, 250); // wait for animation to finish
  };

  return (
    <div className="fixed inset-0 bg-espresso/70 backdrop-blur-sm flex justify-end z-50">
      <div
        className={`
          h-full bg-mocha text-cream flex flex-col border-l border-espresso shadow-xl
          w-[78%] max-w-[900px]
          ${closing ? "animate-slide-out" : "animate-slide-in"}
        `}
      >

        {/* Header */}
        <div className="p-4 border-b border-espresso flex justify-between items-center bg-roast">
          <div className="text-lg font-semibold text-cream">Forked Chat</div>
          <button
            className="text-2xl text-cream hover:text-gold transition"
            onClick={handleClose}
          >
            ×
          </button>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-5 py-4 space-y-2 bg-mocha">
          {(chat?.messages || [])
            .filter((m) => m.role !== "system")
            .map((m) => (
              <MessageBubble
                key={m.id}
                id={m.id}
                role={m.role}
                content={m.content}
                isSecondary={true}
                isThinking={m.isThinking === true}
              />
            ))}
          <div ref={bottomRef} />
        </div>

        {/* Input */}
        <form
          autoComplete="off"
          onSubmit={(e) => {
            e.preventDefault();
            const text = e.target.msg.value;
            if (text.trim()) onSend(text);
            e.target.reset();
          }}
          className="p-4 border-t border-espresso flex gap-3 bg-roast"
        >
          <input
            name="msg"
            autoComplete="off"
            className="
              flex-1 p-3 rounded-xl bg-foam text-cream placeholder-latte
              focus:ring-2 focus:ring-caramel outline-none
            "
            placeholder="Ask further…"
          />

          <button className="px-6 py-3 bg-caramel text-espresso rounded-xl hover:bg-gold transition">
            Send
          </button>
        </form>
      </div>
    </div>
  );
}
