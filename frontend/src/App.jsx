import { useState } from "react";
import "./App.css";

const sessionId = crypto.randomUUID();

export default function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  async function sendMessage(e) {
    e.preventDefault();

    const message = input.trim();
    if (!message || loading) return;

    setMessages((prev) => [...prev, { role: "user", content: message }]);
    setInput("");
    setLoading(true);

    try {
      const response = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: sessionId,
          message,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to get response");
      }

      const data = await response.json();

      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: data.reply },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Unable to connect. Please try again.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="chat">
      <header>
        <h2>AI Chat</h2>
        <p>Multi-turn LLM conversation</p>
      </header>

      <section className="messages">
        {messages.length === 0 && (
          <div className="welcome">
            <h3>How can I help you?</h3>
            <p>Start a conversation with the AI.</p>
          </div>
        )}

        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.role}`}>
            <span>{msg.role === "user" ? "You" : "AI"}</span>
            <p>{msg.content}</p>
          </div>
        ))}

        {loading && <div className="typing">AI is thinking...</div>}
      </section>

      <form onSubmit={sendMessage} className="composer">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Message the AI..."
          disabled={loading}
        />
        <button disabled={loading || !input.trim()}>Send</button>
      </form>
    </main>
  );
}
