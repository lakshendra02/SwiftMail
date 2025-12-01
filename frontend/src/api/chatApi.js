import axios from "axios";

// Set the base URL to your deployed FastAPI backend URL
const API = axios.create({
  baseURL: "https://swiftmail-backend-ty9c.onrender.com/api",
  withCredentials: true, // Important for session cookies
});

export const processCommand = (command) => {
  return API.post("/chat/command", { command });
};

// NEW EXPORT
export const suggestReply = (emailId) => {
  return API.post("/chat/suggest-reply", { email_id: emailId });
};

export const sendReplyConfirmation = (emailId, replyBody) => {
  // Note: API uses 'email_id' and 'reply_body'
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
