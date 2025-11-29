import axios from "axios";

const API = axios.create({
  baseURL: "http://127.0.0.1:8000",
});

// --- Primary chats ---
export const createPrimaryChat = () =>
  API.post("/chats/").then(res => res.data);

export const getChat = (id) =>
  API.get(`/chats/${id}`).then(res => res.data);

export const sendMessage = async (chatId, content) =>
  API.post(`/chats/${chatId}/messages`, {
    role: "user",
    content: content,
  }).then(res => res.data);

// --- Forked chats ---
export const createFork = (parentChatId, parentMessageId) =>
  API.post("/chats/fork", {
    parent_chat_id: parentChatId,
    parent_message_id: parentMessageId,
  }).then(res => res.data);

export const getAllChats = async () => {
  const res = await API.get("/chats/");
  return res.data;
};
