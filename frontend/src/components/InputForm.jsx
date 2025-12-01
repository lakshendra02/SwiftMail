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
      className="p-4 border-t border-gray-200 bg-white shadow-lg flex space-x-3"
    >
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Ask me to read, reply, or delete emails..."
        disabled={loading}
        className="flex-grow p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition duration-150 text-gray-700"
      />
      <button
        type="submit"
        disabled={loading || !input.trim()}
        className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition duration-200 disabled:bg-blue-300 disabled:cursor-not-allowed shadow-md"
      >
        {loading ? "Sending..." : "Send"}
      </button>
    </form>
  );
};

export default InputForm;
