import ReactMarkdown from "react-markdown";
import TypingDots from "./TypingDots";

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

  // ----------------------------------------------------------
  // THINKING BUBBLE (shows partial text + dots)
  // ----------------------------------------------------------
  if (isThinking) {
    return (
      <div className="flex justify-start">
        <div
          className="
            max-w-[75%] rounded-xl px-4 py-2 mb-2
            bg-gray-800 text-gray-100
          "
        >
          {/* STREAMED TEXT (partial) */}
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
          max-w-[75%] rounded-xl px-4 py-2 mb-2
          ${isUser ? "bg-blue-600 text-white"
                   : "bg-gray-800 text-gray-100"}
        `}
      >
        <div className="prose prose-invert max-w-none">
          <ReactMarkdown>{content}</ReactMarkdown>
        </div>

        {isAssistant && !isSecondary && id > 0 && (
          <button
            onClick={onDrillDown}
            className="text-xs text-blue-300 mt-1 hover:underline"
          >
            Drill down →
          </button>
        )}
      </div>
    </div>
  );
}
