import React, { useEffect, useState } from "react";
import { useChatManager } from "./hooks/useChatManager";

import ChatListSidebar from "./components/ChatListSidebar";
import PrimaryChat from "./components/PrimaryChat";
import SecondaryChatOverlay from "./components/SecondaryChatOverlay";
import EnterApiKey from "./components/EnterApiKey";

export default function App() {
  const [apiKey, setApiKey] = useState(null);

  // ---- IMPORTANT FIX ----
  // Always call hooks in the same order
  const {
    chats,
    activeChatId,
    primaryChat,
    secondaryChat,

    loadChat,
    loadChats,
    startNewChat,

    sendPrimaryMessage,
    sendSecondaryMessage,

    openFork,
    closeSecondary,

    goHome,
  } = useChatManager();
  // ------------------------

  // Load API key on startup
  useEffect(() => {
    const stored = sessionStorage.getItem("google_api_key");
    if (stored) setApiKey(stored);
  }, []);

  // Gate UI AFTER calling hooks (avoid hook order change)
  if (!apiKey) {
    return <EnterApiKey onApiKeySaved={setApiKey} />;
  }

  return (
    <div className="flex h-screen bg-espresso text-cream relative">
      {/* Sidebar */}
      <ChatListSidebar
        startNewChat={startNewChat}
        chats={chats}
        activeChatId={activeChatId}
        onSelectChat={loadChat}
        goHome={goHome}
      />

      {/* Primary Chat */}
      <PrimaryChat
        chat={primaryChat}
        onSend={sendPrimaryMessage}
        onDrillDown={openFork}
        onStartNewChat={startNewChat}
      />

      {/* Secondary Overlay */}
      {secondaryChat && (
        <SecondaryChatOverlay
          chat={secondaryChat}
          onSend={sendSecondaryMessage}
          onClose={closeSecondary}
        />
      )}
    </div>
  );
}
