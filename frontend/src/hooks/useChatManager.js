import { useState, useEffect } from "react";
import {
  getAllChats,
  createPrimaryChat,
  getChat,
  sendMessage,
  createFork,
} from "../api/chats";

export function useChatManager() {
  // Sidebar list
  const [chats, setChats] = useState([]);
  const [activeChatId, setActiveChatId] = useState(null);

  // Main chat states
  const [primaryChat, setPrimaryChat] = useState(null);
  const [secondaryChat, setSecondaryChat] = useState(null);

  // -----------------------------------------------------
  // Load chats on startup
  // -----------------------------------------------------
  useEffect(() => {
    loadChats();
  }, []);

  const loadChats = async () => {
    try {
      const all = await getAllChats();
      setChats(all);
    } catch (err) {
      console.error("Failed to load chats:", err);
    }
  };

  // -----------------------------------------------------
  // PRIMARY CHAT
  // -----------------------------------------------------
  const loadChat = async (id) => {
    const chat = await getChat(id);
    setPrimaryChat(chat);
    setActiveChatId(id);
  };

  const startNewChat = async () => {
    const chat = await createPrimaryChat();
    setPrimaryChat(chat);
    setActiveChatId(chat.id);

    setChats((prev) => [chat, ...prev]);
  };

  // -----------------------------------------------------
  // SEND PRIMARY MESSAGE
  // -----------------------------------------------------
  const sendPrimaryMessage = async (content) => {
    if (!primaryChat || !primaryChat.id) return;

    // 1. Optimistic user message
    const userMsg = {
      id: -1,
      role: "user",
      content,
      created_at: new Date().toISOString(),
    };

    // 2. Thinking placeholder
    const thinkingMsg = {
      id: -2,
      role: "assistant",
      content: "",
      isThinking: true,
    };

    // Show user + thinking instantly
    setPrimaryChat((prev) => {
      if (!prev) return prev;
      const prevMessages = prev.messages || [];
      return {
        ...prev,
        messages: [...prevMessages, userMsg, thinkingMsg],
      };
    });

    // 3. Call backend
    const fullChat = await sendMessage(primaryChat.id, content);
    const realAssistant = fullChat.messages[fullChat.messages.length - 1];

    // If backend returned no content, just replace instantly
    if (!realAssistant || typeof realAssistant.content !== "string") {
      setPrimaryChat((prev) => {
        if (!prev || !prev.messages) return prev;
        return {
          ...prev,
          messages: prev.messages.map((m) =>
            m.id === -2 ? { ...realAssistant, isThinking: false } : m
          ),
        };
      });

      setChats((prev) =>
        prev.map((c) => (c.id === fullChat.id ? fullChat : c))
      );

      return;
    }

    // 4. Stream text into the thinking bubble
    simulateTyping(
      realAssistant.content,
      (partial) => {
        setPrimaryChat((prev) => {
          if (!prev || !prev.messages) return prev; // <-- guard
          return {
            ...prev,
            messages: prev.messages.map((m) =>
              m.id === -2 ? { ...m, content: partial } : m
            ),
          };
        });
      },
      () => {
        // 5. Replace placeholder with real message
        setPrimaryChat((prev) => {
          if (!prev || !prev.messages) return prev; // <-- guard
          return {
            ...prev,
            messages: prev.messages.map((m) =>
              m.id === -2 ? realAssistant : m
            ),
          };
        });

        // Update sidebar entry too
        setChats((prev) =>
          prev.map((c) => (c.id === fullChat.id ? fullChat : c))
        );
      }
    );
  };

  // -----------------------------------------------------
  // SECONDARY CHAT (FORKED CHAT)
  // -----------------------------------------------------
  const openFork = async (messageId) => {
    if (!primaryChat || !primaryChat.id) return;

    const fork = await createFork(primaryChat.id, messageId);
    setSecondaryChat(fork);
  };

  const sendSecondaryMessage = async (content) => {
    if (!secondaryChat || !secondaryChat.id) return;

    // 1. Optimistic user msg
    const userMsg = {
      id: -1,
      role: "user",
      content,
      created_at: new Date().toISOString(),
    };

    // 2. Thinking placeholder
    const thinkingMsg = {
      id: -2,
      role: "assistant",
      content: "",
      isThinking: true,
    };

    // Show user + thinking
    setSecondaryChat((prev) => {
      if (!prev) return prev;
      const prevMessages = prev.messages || [];
      return {
        ...prev,
        messages: [...prevMessages, userMsg, thinkingMsg],
      };
    });

    // 3. Call backend
    const fullChat = await sendMessage(secondaryChat.id, content);
    const realAssistant = fullChat.messages[fullChat.messages.length - 1];

    // If empty content, replace instantly
    if (!realAssistant || typeof realAssistant.content !== "string") {
      setSecondaryChat((prev) => {
        if (!prev || !prev.messages) return prev; // guard
        return {
          ...prev,
          messages: prev.messages.map((m) =>
            m.id === -2 ? { ...realAssistant, isThinking: false } : m
          ),
        };
      });
      return;
    }

    // 4. Stream into bubble
    simulateTyping(
      realAssistant.content,
      (partial) => {
        setSecondaryChat((prev) => {
          if (!prev || !prev.messages) return prev; // <-- guard
          return {
            ...prev,
            messages: prev.messages.map((m) =>
              m.id === -2 ? { ...m, content: partial } : m
            ),
          };
        });
      },
      () => {
        setSecondaryChat((prev) => {
          if (!prev || !prev.messages) return prev; // <-- guard
          return {
            ...prev,
            messages: prev.messages.map((m) =>
              m.id === -2 ? realAssistant : m
            ),
          };
        });
      }
    );
  };

  const closeSecondary = () => setSecondaryChat(null);

  // -----------------------------------------------------
  // Return everything UI needs
  // -----------------------------------------------------
  return {
    chats,
    activeChatId,
    loadChats,

    primaryChat,
    loadChat,
    startNewChat,
    sendPrimaryMessage,

    secondaryChat,
    openFork,
    sendSecondaryMessage,
    closeSecondary,
  };
}

// -----------------------------------------------------
// TYPING SIMULATION HELPER
// -----------------------------------------------------
function simulateTyping(fullText, updateChunk, onDone) {
  let i = 0;

  const interval = setInterval(() => {
    // avoid errors when switching chats mid-stream
    if (!fullText || typeof fullText !== "string") {
      clearInterval(interval);
      if (onDone) onDone();
      return;
    }

    i++;
    updateChunk(fullText.slice(0, i));

    if (i >= fullText.length) {
      clearInterval(interval);
      if (onDone) onDone();
    }
  }, 30);
}
