import { useEffect, useRef, useState } from "react";
import "./App.css";

const API_URL = "http://localhost:8000/chat";

function createSessionId() {
  return crypto.randomUUID();
}

export default function App() {
  const [sessionId, setSessionId] = useState(createSessionId);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const inputRef = useRef(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
      block: "end",
    });
  }, [messages, loading]);

  function handleNewChat() {
    if (loading) return;

    setSessionId(createSessionId());
    setMessages([]);
    setInput("");
    inputRef.current?.focus();
  }

  async function handleSend(event) {
    event?.preventDefault();

    const message = input.trim();

    if (!message || loading) return;

    const currentSessionId = sessionId;

    setMessages((previous) => [
      ...previous,
      { role: "user", content: message },
    ]);

    setInput("");
    setLoading(true);

    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          session_id: currentSessionId,
          message,
        }),
      });

      if (!response.ok) {
        let errorMessage = `Request failed (${response.status})`;

        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorMessage;
        } catch {
          // Keep the default error message.
        }

        throw new Error(errorMessage);
      }

      const data = await response.json();

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content: data.reply,
        },
      ]);
    } catch (error) {
      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content: `Unable to connect to the backend. ${
            error.message || "Please check that your server is running."
          }`,
        },
      ]);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  }

  function handleKeyDown(event) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      handleSend();
    }
  }

  return (
    <div className="app-shell">
      <main className="main-panel">
        <header className="topbar">
          <h1 className="brand">Chatbot</h1>

          <button
            className="new-chat-button"
            type="button"
            onClick={handleNewChat}
            disabled={loading}
          >
            + New chat
          </button>
        </header>

        <section
          className={`conversation ${messages.length ? "has-messages" : ""}`}
        >
          {messages.length === 0 ? (
            <h2 className="welcome-title">What can I help you with?</h2>
          ) : (
            <div className="message-list">
              {messages.map((message, index) => (
                <article
                  className={`chat-message ${message.role}`}
                  key={`${index}-${message.role}`}
                >
                  {message.role === "assistant" && (
                    <div className="assistant-mark">✳</div>
                  )}

                  <div className="message-content">{message.content}</div>
                </article>
              ))}

              {loading && (
                <article className="chat-message assistant">
                  <div className="assistant-mark">✳</div>

                  <div className="message-content typing">
                    <span />
                    <span />
                    <span />
                  </div>
                </article>
              )}

              <div ref={messagesEndRef} />
            </div>
          )}
        </section>

        <div className="composer-area">
          <form className="composer" onSubmit={handleSend}>
            <textarea
              ref={inputRef}
              value={input}
              onChange={(event) => setInput(event.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Message your chatbot..."
              aria-label="Message"
              rows={1}
              disabled={loading}
            />

            <button
              className="send-button"
              type="submit"
              disabled={loading || !input.trim()}
              aria-label="Send message"
            >
              {loading ? (
                <span className="send-spinner" />
              ) : (
                <svg viewBox="0 0 24 24" aria-hidden="true">
                  <path d="M12 19V5M6 11l6-6 6 6" />
                </svg>
              )}
            </button>
          </form>

          <p className="disclaimer">
            AI can make mistakes. Check important information.
          </p>
        </div>
      </main>
    </div>
  );
}
