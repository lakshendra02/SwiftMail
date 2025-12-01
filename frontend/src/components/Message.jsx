import React from "react";
import { suggestReply } from "../api/chatApi";

const Message = ({ sender, text, isSystem, data, action, onAction }) => {
  const isAI = sender === "AI" || isSystem;

  const messageContainerClass = isAI
    ? "flex justify-start mb-4"
    : "flex justify-end mb-4";

  const messageBubbleClass = isAI
    ? "bg-gray-100 text-gray-800 rounded-2xl rounded-tl-none p-4 max-w-xl shadow-sm backdrop-blur-sm"
    : "bg-blue-600 text-white rounded-2xl rounded-tr-none p-4 max-w-xl shadow-md";

  const handleSuggestReply = async (emailId) => {
    try {
      onAction("status_update", {
        text: `AI is generating a reply for email ${emailId.substring(
          0,
          5
        )}...`,
      });
      const response = await suggestReply(emailId);
      const { proposed_reply, original_email_id } = response.data.data;

      onAction("reply_suggested", {
        text: `<strong>Draft Reply:</strong><br><br><pre>${proposed_reply}</pre><br>Confirm sending this reply?`,
        data: {
          original_email_id: original_email_id,
          reply_body: proposed_reply,
        },
      });
    } catch (error) {
      onAction("status_update", {
        text: `Failed to suggest reply: ${
          error.response?.data?.detail || "Server error"
        }`,
        isError: true,
      });
    }
  };

  const handlePreDelete = (emailId) => {
    onAction("pre_delete", { email_id: emailId });
  };

  const renderDeleteConfirmation = () => {
    if (action === "confirm_delete" && data && data.email_id) {
      return (
        <div className="mt-3 p-4 bg-red-50 border border-red-300 text-red-700 rounded-xl text-sm shadow-sm">
          <p className="font-semibold mb-3">
            Are you sure you want to delete this email?
          </p>
          <div className="flex gap-2">
            <button
              onClick={() =>
                onAction("execute_delete", { email_id: data.email_id })
              }
              className="text-xs bg-red-600 hover:bg-red-700 text-white font-medium py-1.5 px-3 rounded-lg transition"
            >
              Yes, Delete
            </button>
            <button
              onClick={() =>
                onAction("status_update", { text: "Deletion cancelled." })
              }
              className="text-xs bg-gray-400 hover:bg-gray-500 text-white font-medium py-1.5 px-3 rounded-lg transition"
            >
              Cancel
            </button>
          </div>
        </div>
      );
    }
    return null;
  };

  const renderSendConfirmation = () => {
    if (action === "confirm_send" && data && data.original_email_id) {
      return (
        <div className="mt-3 p-4 bg-blue-50 border border-blue-300 text-blue-700 rounded-xl text-sm shadow-sm">
          <p className="font-semibold mb-3">Ready to send this AI draft?</p>
          <button
            onClick={() => onAction("confirm_send", data)}
            className="text-xs bg-blue-600 hover:bg-blue-700 text-white font-medium py-1.5 px-3 rounded-lg transition"
          >
            Yes, Send
          </button>
        </div>
      );
    }
    return null;
  };

  const renderEmailSummaries = (emails) => (
    <div className="mt-4 p-4 bg-white/60 backdrop-blur-sm rounded-2xl border border-gray-200 shadow-inner">
      <h3 className="text-lg font-semibold mb-4 text-gray-800">
        Fetched Emails
      </h3>
      {emails.map((email, i) => (
        <div
          key={email.id}
          className="p-4 mb-3 last:mb-0 border border-gray-200 bg-gray-50 rounded-xl shadow-sm"
        >
          <p className="text-sm font-semibold text-blue-600 mb-1">
            Email #{i + 1}
          </p>
          <p className="text-gray-700 text-sm">
            <span className="font-medium">From:</span> {email.sender}
          </p>
          <p className="text-gray-700 text-sm mb-2">
            <span className="font-medium">Subject:</span> {email.subject}
          </p>
          <div className="bg-green-100 p-3 rounded-lg text-sm text-green-800 mb-3">
            <span className="font-semibold">Summary:</span> {email.summary}
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => handleSuggestReply(email.id)}
              className="text-xs bg-indigo-500 hover:bg-indigo-600 text-white font-medium py-1.5 px-3 rounded-lg transition"
            >
              Suggest Reply
            </button>
            <button
              onClick={() => handlePreDelete(email.id)}
              className="text-xs bg-red-500 hover:bg-red-600 text-white font-medium py-1.5 px-3 rounded-lg transition"
            >
              Delete
            </button>
          </div>
        </div>
      ))}
    </div>
  );

  return (
    <div className={messageContainerClass}>
      <div className={messageBubbleClass}>
        <p
          className="whitespace-pre-wrap leading-relaxed"
          dangerouslySetInnerHTML={{
            __html: text.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>"),
          }}
        />
        {action === "read_success" &&
          data?.emails &&
          renderEmailSummaries(data.emails)}
        {renderDeleteConfirmation()}
        {renderSendConfirmation()}
      </div>
    </div>
  );
};

export default Message;
