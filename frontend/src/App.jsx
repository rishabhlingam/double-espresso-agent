import React from "react";
import { useChatManager } from "./hooks/useChatManager";

import ChatListSidebar from "./components/ChatListSidebar";
import PrimaryChat from "./components/PrimaryChat";
import SecondaryChatOverlay from "./components/SecondaryChatOverlay";

export default function App() {
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

      {/* Secondary Overlay (slides over primary) */}
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
