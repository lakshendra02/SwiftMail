import React, { useState, useEffect } from "react";
import {
  processCommand,
  getUserProfile,
  sendReplyConfirmation,
  deleteEmailConfirmation,
} from "../api/chatApi";
import Message from "../components/Message";
import InputForm from "../components/InputForm";

const initialMessages = [
  { sender: "AI", text: "Loading profile...", isSystem: true, id: Date.now() },
];

const ChatbotDashboard = () => {
  const [messages, setMessages] = useState(initialMessages);
  const [loading, setLoading] = useState(false);
  // emailsInView is currently unused but kept for future "delete by number" logic
  // eslint-disable-next-line no-unused-vars
  const [emailsInView, setEmailsInView] = useState([]);

  // Auto-scroll effect
  useEffect(() => {
    const messageContainer = document.getElementById("message-container");
    if (messageContainer) {
      // Scroll smoothly to the last message
      messageContainer.scrollTo({
        top: messageContainer.scrollHeight,
        behavior: "smooth",
      });
    }
  }, [messages, loading]);

  // Initial setup: Fetch user info and greet
  useEffect(() => {
    const fetchWelcomeMessage = async () => {
      try {
        const response = await getUserProfile();
        const { name } = response.data;
        setMessages([
          {
            sender: "AI",
            text: `Hello, **${name}**! I'm your AI Email Assistant. I can read, reply, and delete emails. Try typing: "Read my last 5 emails".`,
            isSystem: true,
            id: Date.now(),
          },
        ]);
      } catch (error) {
        console.error("Failed to load user profile:", error);
        setMessages([
          {
            sender: "AI",
            text: "🔴 Error: Session expired. Please log in again.",
            isSystem: true,
            id: Date.now(),
          },
        ]);
      }
    };
    fetchWelcomeMessage();
  }, []);

  const handleSend = async (userCommand) => {
    setMessages((prev) => [
      ...prev,
      {
        sender: "User",
        text: userCommand,
        isSystem: false,
        id: Date.now() + 1,
      },
    ]);
    setLoading(true);

    try {
      const response = await processCommand(userCommand);
      const { response: aiResponse, action, data } = response.data;

      if (action === "read_success" && data && data.emails) {
        setEmailsInView(data.emails);
      }

      setMessages((prev) => [
        ...prev,
        {
          sender: "AI",
          text: aiResponse,
          isSystem: true,
          data: data,
          action: action,
          id: Date.now() + 2,
        },
      ]);
    } catch (error) {
      const errorMessage =
        error.response?.data?.detail || "An unexpected API error occurred.";
      setMessages((prev) => [
        ...prev,
        {
          sender: "AI",
          text: `🔴 Error: ${errorMessage}`,
          isSystem: true,
          id: Date.now() + 2,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  // Handles button clicks and status updates from the Message component
  const handleAction = async (actionType, data) => {
    // Status update from child component (e.g., temporary loading message from AI service)
    if (actionType === "status_update") {
      setMessages((prev) => [
        ...prev,
        {
          sender: "AI",
          text: data.text,
          isSystem: true,
          id: Date.now() + 5,
        },
      ]);
      return;
    }

    // New action: Proposed reply is ready to be confirmed
    if (actionType === "reply_suggested") {
      setMessages((prev) => [
        ...prev,
        {
          sender: "AI",
          text: data.text,
          isSystem: true,
          action: "confirm_send", // Triggers the confirmation button in Message.jsx
          data: data.data,
          id: Date.now() + 5,
        },
      ]);
      return;
    }

    // --- EXECUTE FINAL API ACTIONS ---
    setLoading(true);
    let apiCall;
    let successMessage;

    if (actionType === "confirm_send") {
      apiCall = sendReplyConfirmation(data.original_email_id, data.reply_body);
      successMessage = "✅ Reply sent successfully!";
    } else if (actionType === "confirm_delete") {
      const emailIdToDelete = data.email_id;
      apiCall = deleteEmailConfirmation(emailIdToDelete);
      successMessage =
        "🗑️ Email deleted successfully! (ID: " +
        emailIdToDelete.substring(0, 10) +
        "...)";
    } else {
      setLoading(false);
      return;
    }

    try {
      // Show transient status update (using a placeholder)
      setMessages((prev) => [
        ...prev,
        {
          sender: "AI",
          text: `Executing ${actionType.replace("_", " ")}...`,
          isSystem: true,
          id: Date.now() + 6,
        },
      ]);

      await apiCall;
      setMessages((prev) => [
        ...prev,
        {
          sender: "AI",
          text: successMessage,
          isSystem: true,
          id: Date.now() + 7,
        },
      ]);
    } catch (error) {
      // Use the specific detail from the backend for the error message
      const errorMessage =
        error.response?.data?.detail || "Server error during execution.";
      setMessages((prev) => [
        ...prev,
        {
          sender: "AI",
          text: `❌ Action failed: ${errorMessage}`,
          isSystem: true,
          id: Date.now() + 7,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-100">
      <header className="bg-white p-4 shadow-md flex justify-between items-center border-b border-gray-200">
        <h1 className="text-xl font-bold text-gray-800">
          Constructure AI Assistant
        </h1>
        <button
          onClick={() =>
            (window.location.href = "http://localhost:8000/api/auth/logout")
          }
          className="text-sm bg-red-500 hover:bg-red-600 text-white py-1 px-3 rounded transition"
        >
          Logout
        </button>
      </header>

      <div
        id="message-container"
        className="flex-grow p-6 overflow-y-auto space-y-4"
      >
        {messages.map((msg) => (
          <Message key={msg.id} {...msg} onAction={handleAction} />
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-yellow-100 text-yellow-800 rounded-bl-xl rounded-tr-xl rounded-br-xl p-3 text-sm italic shadow-md">
              ...Working on it...
            </div>
          </div>
        )}
      </div>

      <InputForm onSend={handleSend} loading={loading} />
    </div>
  );
};

export default ChatbotDashboard;
