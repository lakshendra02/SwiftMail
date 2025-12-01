import React, { useState } from "react";

const InputForm = ({ onSend, loading }) => {
  const [input, setInput] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    onSend(input);
    setInput("");
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="p-4 border-t border-gray-300 bg-white shadow-xl flex items-center space-x-3"
    >
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Type your message..."
        disabled={loading}
        className="flex-grow p-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 transition text-gray-800 placeholder-gray-400"
      />
      <button
        type="submit"
        disabled={loading || !input.trim()}
        className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-6 rounded-xl transition disabled:bg-blue-300 disabled:cursor-not-allowed shadow-md"
      >
        {loading ? "Sending" : "Send"}
      </button>
    </form>
  );
};

export default InputForm;
