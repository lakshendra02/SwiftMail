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
  const [emailsInView, setEmailsInView] = useState([]);

  useEffect(() => {
    const container = document.getElementById("message-container");
    if (container)
      container.scrollTo({ top: container.scrollHeight, behavior: "smooth" });
  }, [messages, loading]);

  useEffect(() => {
    const loadUser = async () => {
      try {
        const response = await getUserProfile();
        const { name } = response.data;
        setMessages([
          {
            sender: "AI",
            text: `Hello, ${name}. I can read, reply, and delete emails. Try typing: Read my last 5 emails.`,
            isSystem: true,
            id: Date.now(),
          },
        ]);
      } catch (error) {
        setMessages([
          {
            sender: "AI",
            text: "Error: Session expired. Please log in again.",
            isSystem: true,
            id: Date.now(),
          },
        ]);
      }
    };
    loadUser();
  }, []);

  const handleSend = async (command) => {
    setMessages((prev) => [
      ...prev,
      { sender: "User", text: command, isSystem: false, id: Date.now() + 1 },
    ]);
    setLoading(true);

    try {
      const response = await processCommand(command);
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
      const err =
        error.response?.data?.detail || "An unexpected error occurred.";
      setMessages((prev) => [
        ...prev,
        {
          sender: "AI",
          text: `Error: ${err}`,
          isSystem: true,
          id: Date.now() + 2,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleAction = async (type, data) => {
    if (type === "status_update") {
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

    if (type === "reply_suggested") {
      setMessages((prev) => [
        ...prev,
        {
          sender: "AI",
          text: data.text,
          isSystem: true,
          action: "confirm_send",
          data: data.data,
          id: Date.now() + 5,
        },
      ]);
      return;
    }

    if (type === "pre_delete") {
      setMessages((prev) => [
        ...prev,
        {
          sender: "AI",
          text: "Please confirm deletion for the selected email.",
          isSystem: true,
          action: "confirm_delete",
          data: { email_id: data.email_id },
          id: Date.now() + 5,
        },
      ]);
      return;
    }

    setLoading(true);
    let apiCall;
    let successMessage;

    if (type === "confirm_send") {
      apiCall = sendReplyConfirmation(data.original_email_id, data.reply_body);
      successMessage = "Reply sent successfully.";
    } else if (type === "execute_delete") {
      apiCall = deleteEmailConfirmation(data.email_id);
      successMessage = "Email deleted successfully.";
    } else {
      setLoading(false);
      return;
    }

    try {
      setMessages((prev) => [
        ...prev,
        {
          sender: "AI",
          text: `Executing ${type.replace("_", " ")}...`,
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
      const err =
        error.response?.data?.detail || "Server error during execution.";
      setMessages((prev) => [
        ...prev,
        {
          sender: "AI",
          text: `Action failed: ${err}`,
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
        <h1 className="text-xl font-semibold text-gray-800">
          SwiftMail - AI Email Assistant
        </h1>
        <button
          onClick={() =>
            (window.location.href =
              "https://swiftmail-backend-ty9c.onrender.com//api/auth/logout")
          }
          className="text-sm bg-red-600 hover:bg-red-700 text-white py-1.5 px-4 rounded-lg transition"
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
            <div className="bg-yellow-100 text-yellow-800 rounded-xl p-3 text-sm shadow-sm">
              Processing request...
            </div>
          </div>
        )}
      </div>

      <InputForm onSend={handleSend} loading={loading} />
    </div>
  );
};

export default ChatbotDashboard;
