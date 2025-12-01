import React from "react";
import { suggestReply } from "../api/chatApi";

const Message = ({ sender, text, isSystem, data, action, onAction, index }) => {
  const isAI = sender === "AI" || isSystem;

  const messageContainerClass = isAI
    ? "flex justify-start mb-4"
    : "flex justify-end mb-4";

  const messageBubbleClass = isAI
    ? "bg-gray-200 text-gray-800 rounded-bl-xl rounded-tr-xl rounded-br-xl p-4 max-w-lg shadow-md"
    : "bg-blue-500 text-white rounded-tl-xl rounded-tr-xl rounded-bl-xl p-4 max-w-lg shadow-md";

  const handleSuggestReply = async (emailId) => {
    try {
      // 1. Show transient status update
      onAction("status_update", {
        text: `AI is generating a reply for email ${emailId.substring(
          0,
          5
        )}...`,
      });

      // 2. Call the API
      const response = await suggestReply(emailId);
      const { proposed_reply, original_email_id } = response.data.data;

      // 3. Send the proposed reply message back to the dashboard state for display
      onAction("reply_suggested", {
        text: `📝 **Draft Reply:** \n\n\`\`\`\n${proposed_reply}\n\`\`\`\n\n**Confirm sending this reply?**`,
        data: {
          original_email_id: original_email_id,
          reply_body: proposed_reply,
        },
      });
    } catch (error) {
      onAction("status_update", {
        text: `🔴 Failed to suggest reply: ${
          error.response?.data?.detail || "Server error"
        }`,
        isError: true,
      });
    }
  };

  const renderEmailSummaries = (emails) => (
    <div className="mt-4 p-4 bg-white/70 backdrop-blur-sm rounded-lg border border-gray-300 shadow-inner">
      <h3 className="text-lg font-semibold mb-3 text-gray-800">
        Fetched Emails:
      </h3>
      {emails.map((email, i) => (
        <div
          key={email.id}
          className="email-card p-3 mb-3 last:mb-0 border-b border-gray-200 bg-gray-50 rounded-md"
        >
          <p className="font-bold text-sm text-blue-600 mb-1">Email #{i + 1}</p>
          <p className="text-gray-700">
            📧 <span className="font-medium">From:</span> {email.sender}
          </p>
          <p className="text-gray-700 mb-2">
            Subject: <span className="font-semibold">{email.subject}</span>
          </p>

          <div className="bg-green-100 p-2 rounded text-sm text-green-800 italic">
            <span className="font-bold">Summary:</span> {email.summary}
          </div>

          <div className="mt-3 flex space-x-2">
            <button
              onClick={() => handleSuggestReply(email.id)}
              className="text-xs bg-indigo-500 hover:bg-indigo-600 text-white font-medium py-1 px-2 rounded transition"
            >
              Suggest Reply
            </button>

            <button
              onClick={() => onAction("confirm_delete", { email_id: email.id })}
              className="text-xs bg-red-500 hover:bg-red-600 text-white font-medium py-1 px-2 rounded transition"
            >
              Delete
            </button>
          </div>
        </div>
      ))}
    </div>
  );

  const renderActionConfirmation = () => {
    if (action === "confirm_send" && data && data.original_email_id) {
      return (
        <div className="mt-3 p-3 bg-blue-100 border-l-4 border-blue-500 text-blue-700 rounded-md text-sm">
          <p className="font-bold mb-2">Ready to send this AI draft?</p>
          <button
            onClick={() => onAction("confirm_send", data)}
            className="text-xs bg-blue-600 hover:bg-blue-700 text-white font-medium py-1 px-3 rounded transition mr-2"
          >
            Yes, Send It!
          </button>
        </div>
      );
    }

    // Render other confirmations if needed (e.g., delete confirmation after natural language parsing)
    return null;
  };

  return (
    <div className={messageContainerClass}>
      <div className={messageBubbleClass}>
        <p
          className="message-text whitespace-pre-wrap"
          dangerouslySetInnerHTML={{
            __html: text.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>"),
          }}
        ></p>

        {action === "read_success" &&
          data &&
          data.emails &&
          renderEmailSummaries(data.emails)}

        {renderActionConfirmation()}
      </div>
    </div>
  );
};

export default Message;
