import React from "react";

const Message = ({ sender, text, isSystem, data, action, onAction, index }) => {
  const isAI = sender === "AI" || isSystem;

  // Conditional styling for message bubbles
  const messageContainerClass = isAI
    ? "flex justify-start mb-4"
    : "flex justify-end mb-4";

  const messageBubbleClass = isAI
    ? "bg-gray-200 text-gray-800 rounded-bl-xl rounded-tr-xl rounded-br-xl p-4 max-w-lg shadow-md"
    : "bg-blue-500 text-white rounded-tl-xl rounded-tr-xl rounded-bl-xl p-4 max-w-lg shadow-md";

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
              onClick={() =>
                console.log("Trigger reply generation for ID:", email.id)
              }
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
    if (action === "needs_refinement" && data.intent) {
      const intent = data.intent.action;
      const target =
        data.intent.params.sender ||
        data.intent.params.subject_keyword ||
        data.intent.params.email_number;
      return (
        <div className="mt-3 p-3 bg-yellow-100 border-l-4 border-yellow-500 text-yellow-700 rounded-md text-sm">
          <p>
            I detected the intent to **{intent}** the email related to **"
            {target}"**.
          </p>
          <p className="mt-1 font-semibold">
            Please confirm the target email number or refine your command.
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className={messageContainerClass}>
      <div className={messageBubbleClass}>
        {/* Use dangerouslySetInnerHTML for markdown-style bolding */}
        <p
          className="message-text"
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
