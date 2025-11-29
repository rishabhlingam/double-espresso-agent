import { useEffect, useRef, useState } from "react";
import MessageBubble from "./MessageBubble";

export default function SecondaryChatOverlay({ chat, onSend, onClose }) {
  const bottomRef = useRef(null);
  const [closing, setClosing] = useState(false);

  // Auto-scroll on new messages
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chat?.messages]);

  // Close on ESC
  useEffect(() => {
    const handler = (e) => {
      if (e.key === "Escape") handleClose();
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, []);

  const handleClose = () => {
    setClosing(true);
    setTimeout(onClose, 250); // wait for closing animation
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex justify-end z-50">
      <div
        className={`
          h-full bg-gray-900 text-white flex flex-col border-l border-gray-800 shadow-xl
          w-[78%]                /* <--- wider panel (almost full) */
          max-w-[900px]          /* <--- optional max width */
          ${closing ? "animate-slide-out" : "animate-slide-in"}
        `}
      >

        {/* Header */}
        <div className="p-4 border-b border-gray-800 flex justify-between items-center">
          <div className="text-lg font-semibold text-gray-200">Forked Chat</div>
          <button
            className="text-2xl hover:text-gray-400"
            onClick={handleClose}
          >
            ×
          </button>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-5 py-4 space-y-2">
          {(chat?.messages || [])
            .filter((m) => m.role !== "system")      // hide system prompt
            .map((m) => (
              <MessageBubble
                key={m.id}
                id={m.id}
                role={m.role}
                content={m.content}
                isSecondary={true}                  // hides drill-down
                isThinking={m.isThinking === true}
              />
            ))}
          <div ref={bottomRef} />
        </div>

        {/* Input */}
        <form
          autoComplete="off"                        // prevent prompt history
          onSubmit={(e) => {
            e.preventDefault();
            const text = e.target.msg.value;
            if (text.trim()) onSend(text);
            e.target.reset();
          }}
          className="p-4 border-t border-gray-800 flex gap-3"
        >
          <input
            name="msg"
            autoComplete="off"
            className="flex-1 p-3 rounded-xl bg-gray-800 text-white
                       focus:ring-2 focus:ring-blue-600 outline-none"
            placeholder="Ask further…"
          />

          <button className="px-6 py-3 bg-blue-600 rounded-xl hover:bg-blue-700 transition">
            Send
          </button>
        </form>
      </div>
    </div>
  );
}
