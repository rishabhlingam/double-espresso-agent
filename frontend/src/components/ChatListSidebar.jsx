export default function ChatListSidebar({
  startNewChat,
  chats,
  activeChatId,
  onSelectChat,
}) {
  // Only primary chats
  const primaryChats = chats.filter((c) => c.type === "primary");

  return (
    <div className="w-64 bg-roast text-cream border-r border-espresso p-4 flex flex-col">

      {/* Project Title */}
      <div className="mb-4">
        <h1 className="text-xl font-semibold text-cream">Double Espresso Agent</h1>
      </div>

      {/* New Chat Button */}
      <button
        className="px-4 py-3 bg-caramel text-espresso rounded-lg mb-6 text-left font-medium
                   hover:bg-gold transition"
        onClick={startNewChat}
      >
        + New Chat
      </button>

      {/* Chat List */}
      <div className="flex-1 overflow-y-auto space-y-1">

        {primaryChats.length === 0 && (
          <div className="text-latte text-sm">No chats yet. Start one!</div>
        )}

        {primaryChats.map((chat) => {
          // Find the first user message
          const firstUserMessage = chat.messages?.find(
            (m) => m.role === "user"
          )?.content;

          const preview = firstUserMessage
            ? firstUserMessage.split("\n")[0].slice(0, 60) // limit preview length
            : "New Chat";

          return (
            <button
              key={chat.id}
              onClick={() => onSelectChat(chat.id)}
              className={`w-full text-left px-3 py-2 rounded-md text-sm truncate transition
                ${
                  chat.id === activeChatId
                    ? "bg-mocha text-cream"
                    : "text-latte hover:bg-foam/50"
                }
              `}
            >
              {preview}
            </button>
          );
        })}
      </div>
    </div>
  );
}
