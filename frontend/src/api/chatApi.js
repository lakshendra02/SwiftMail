// frontend/src/api/chatApi.js
import axios from "axios";

// Set the base URL to your deployed FastAPI backend URL
const API = axios.create({
  baseURL: "http://localhost:8000/api",
  withCredentials: true, // Important for session cookies
});

export const processCommand = (command) => {
  return API.post("/chat/command", { command });
};

export const sendReplyConfirmation = (emailId, replyBody) => {
  return API.post("/chat/send-reply", {
    email_id: emailId,
    reply_body: replyBody,
  });
};

export const deleteEmailConfirmation = (emailId) => {
  return API.post("/chat/delete-email", { email_id: emailId });
};

export const getUserProfile = () => {
  return API.get("/chat/user/profile");
};
