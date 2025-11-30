import ReactMarkdown from "react-markdown";
import TypingDots from "./TypingDots";
import { ClipboardIcon, MagnifyingGlassIcon } from "@heroicons/react/24/outline";

export default function MessageBubble({
  id,
  role,
  content,
  onDrillDown,
  isSecondary,
  isThinking,
}) {
  const isUser = role === "user";
  const isAssistant = role === "assistant";

  const handleCopy = () => {
    navigator.clipboard.writeText(content);
  };

  // ----------------------------------------------------------
  // THINKING BUBBLE
  // ----------------------------------------------------------
  if (isThinking) {
    return (
      <div className="flex justify-start">
        <div
          className="
            max-w-[75%] rounded-xl px-4 py-2 mb-2
            bg-foam text-cream shadow-md shadow-espresso/40
          "
        >
          {/* STREAMED PARTIAL TEXT */}
          {content && (
            <div className="prose prose-invert max-w-none mb-1">
              <ReactMarkdown>{content}</ReactMarkdown>
            </div>
          )}

          {/* DOTS */}
          <TypingDots />
        </div>
      </div>
    );
  }

  // ----------------------------------------------------------
  // NORMAL BUBBLE
  // ----------------------------------------------------------
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`
          max-w-[75%] rounded-xl px-4 py-2 mb-2 shadow-md
          ${isUser
            ? "bg-caramel text-espresso shadow-caramel/30"
            : "bg-foam text-cream shadow-espresso/40"
          }
        `}
      >
        {/* MARKDOWN TEXT */}
        <div className="prose prose-invert max-w-none">
          <ReactMarkdown>{content}</ReactMarkdown>
        </div>

        {/* DRILL DOWN BUTTON (assistant only, not secondary) */}
        {isAssistant && !isSecondary && id > 0 && (
          <button
            onClick={onDrillDown}
            className="text-xs text-gold mt-1 hover:underline"
          >
            <MagnifyingGlassIcon className="w-4 h-4" />
          </button>
        )}

        {isAssistant && (
          <button
          onClick={handleCopy}
          className="text-xs text-latte mt-1 ml-2 hover:text-gold transition"
          >
            <ClipboardIcon className="w-4 h-4" />
          </button>
        )}

      </div>
    </div>
  );
}
