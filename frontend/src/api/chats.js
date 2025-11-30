import axios from "axios";

// Helper to get user-provided API key from browser storage
function getApiKey() {
  return sessionStorage.getItem("google_api_key") || "";
}

// Axios instance
const API = axios.create({
  baseURL: "http://127.0.0.1:8000",
});

// Attach API key to every request automatically
API.interceptors.request.use((config) => {
  const apiKey = getApiKey();
  if (apiKey) {
    config.headers["x-user-api-key"] = apiKey;
  }
  return config;
});

// --- Primary chats ---
export const createPrimaryChat = () =>
  API.post("/chats/").then((res) => res.data);

export const getChat = (id) =>
  API.get(`/chats/${id}`).then((res) => res.data);

export const sendMessage = async (chatId, content) =>
  API.post(`/chats/${chatId}/messages`, {
    role: "user",
    content: content,
  }).then((res) => res.data);

// --- Forked chats ---
export const createFork = (parentChatId, parentMessageId) =>
  API.post("/chats/fork", {
    parent_chat_id: parentChatId,
    parent_message_id: parentMessageId,
  }).then((res) => res.data);

export const getAllChats = async () => {
  const res = await API.get("/chats/");
  return res.data;
};
