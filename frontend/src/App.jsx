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

  // We never early-return EnterApiKey — we overlay it instead
  const isApiKeyMissing = !apiKey;

  return (
    <div className="relative h-screen w-screen overflow-hidden">

      {/* ---- MAIN APP UI (always rendered, blurred if no API key) ---- */}
      <div
        className={`h-full transition-all duration-300 ${
          isApiKeyMissing ? "filter blur-md pointer-events-none" : ""
        }`}
      >
        <div className="flex h-full bg-espresso text-cream relative">
          <ChatListSidebar
            startNewChat={startNewChat}
            chats={chats}
            activeChatId={activeChatId}
            onSelectChat={loadChat}
            goHome={goHome}
          />

          <PrimaryChat
            chat={primaryChat}
            onSend={sendPrimaryMessage}
            onDrillDown={openFork}
            onStartNewChat={startNewChat}
          />

          {secondaryChat && (
            <SecondaryChatOverlay
              chat={secondaryChat}
              onSend={sendSecondaryMessage}
              onClose={closeSecondary}
            />
          )}
        </div>
      </div>

      {/* ---- API KEY MODAL OVERLAY ---- */}
      {isApiKeyMissing && (
        <div className="absolute inset-0 flex justify-center items-center bg-black/40 backdrop-blur-sm z-10">
          <EnterApiKey onApiKeySaved={setApiKey} />
        </div>
      )}
    </div>
  );
}
