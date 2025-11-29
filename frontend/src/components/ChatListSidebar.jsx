export default function ChatListSidebar({
  startNewChat,
  chats,
  activeChatId,
  onSelectChat,
}) {
  // Only primary chats
  const primaryChats = chats.filter((c) => c.type === "primary");

  return (
    <div className="w-64 bg-gray-950 text-white border-r border-gray-800 p-4 flex flex-col">

      {/* New Chat Button */}
      <button
        className="px-4 py-3 bg-blue-600 rounded-lg mb-6 text-left font-medium
                   hover:bg-blue-700 transition"
        onClick={startNewChat}
      >
        + New Chat
      </button>

      {/* Chat List */}
      <div className="flex-1 overflow-y-auto space-y-1">

        {primaryChats.length === 0 && (
          <div className="text-gray-400 text-sm">No chats yet. Start one!</div>
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
                    ? "bg-gray-800 text-white"
                    : "text-gray-300 hover:bg-gray-800/70"
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
