import { useEffect, useRef, useState, useCallback } from "react";
import Auth from "./components/Auth";
import { chatApi, ragApi } from "./services/api";
import "./App.css";

export default function App() {
  const [token, setToken] = useState(
    () => localStorage.getItem("token") || null,
  );
  const [userName, setUserName] = useState(
    () => localStorage.getItem("userName") || "",
  );

  const [sessionId, setSessionId] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [uploadedFile, setUploadedFile] = useState(null);

  const inputRef = useRef(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
      block: "end",
    });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading, scrollToBottom]);

  // Fetch past sessions when authenticated
  const loadSessions = useCallback(async () => {
    if (!token) return;
    try {
      const data = await chatApi.getSessions();
      setSessions(data);
    } catch (err) {
      console.error("Failed to load sessions:", err);
    }
  }, [token]);

  useEffect(() => {
    loadSessions();
  }, [loadSessions]);

  async function handleSelectSession(targetSessionId) {
    if (loading || targetSessionId === sessionId) return;
    setLoading(true);
    try {
      const data = await chatApi.getSessionHistory(targetSessionId);
      setSessionId(data.session_id);
      setMessages(data.messages);
    } catch (err) {
      console.error("Failed to load session history:", err);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  }

  function handleLoginSuccess(data) {
    localStorage.setItem("token", data.access_token);
    localStorage.setItem("userName", data.user_name || "User");
    setToken(data.access_token);
    setUserName(data.user_name || "User");
  }

  function handleLogout() {
    localStorage.removeItem("token");
    localStorage.removeItem("userName");
    setToken(null);
    setUserName("");
    setSessionId(null);
    setMessages([]);
    setSessions([]);
  }

  function handleNewChat() {
    if (loading) return;
    setSessionId(null);
    setMessages([]);
    setInput("");
    inputRef.current?.focus();
  }

  async function handleSend(event) {
    event?.preventDefault();
    const message = input.trim();
    if (!message || loading) return;

    const currentSessionId = sessionId;
    setMessages((prev) => [...prev, { role: "user", content: message }]);
    setInput("");
    setLoading(true);

    try {
      const data = await chatApi.sendMessage({
        session_id: currentSessionId,
        message,
      });

      if (!sessionId && data.session_id) {
        setSessionId(data.session_id);
      }

      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: data.reply },
      ]);
      loadSessions(); // Refresh sidebar history list
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `Unable to connect to the backend: ${error.message}`,
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

  if (!token) {
    return <Auth onLoginSuccess={handleLoginSuccess} />;
  }

  async function handleFileChange(event) {
    const file = event.target.files?.[0];
    if (!file) return;

    try {
      setLoading(true);
      const data = await ragApi.uploadPdf(file, sessionId);
      if (!sessionId && data.session_id) {
        setSessionId(data.session_id);
      }
      setUploadedFile(file.name);
    } catch (err) {
      alert(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleRemovePdf() {
    if (!sessionId) return;
    try {
      await ragApi.deleteSessionDocs(sessionId);
      setUploadedFile(null);
    } catch (err) {
      console.error("Failed to delete PDF:", err);
    }
  }

  return (
    <div className="app-shell">
      <aside className={`sidebar ${sidebarOpen ? "open" : "closed"}`}>
        <div className="sidebar-top">
          <h1 className="brand">Chatbot</h1>
          <button
            className="new-chat-button"
            type="button"
            onClick={handleNewChat}
            disabled={loading}
          >
            + New chat
          </button>
        </div>

        {/* Recent Chat History Section */}
        <div className="sidebar-history">
          <span className="history-label">Recent Chats</span>
          <div className="history-list">
            {sessions.map((s) => (
              <button
                key={s.session_id}
                className={`history-item ${sessionId === s.session_id ? "active" : ""}`}
                onClick={() => handleSelectSession(s.session_id)}
                type="button"
              >
                {s.title}
              </button>
            ))}
          </div>
        </div>

        <div className="sidebar-bottom">
          <div className="user-profile-info">
            <span className="user-avatar">
              {userName ? userName[0].toUpperCase() : "U"}
            </span>
            <span className="user-name">{userName || "User"}</span>
          </div>
          <button
            className="logout-button"
            type="button"
            onClick={handleLogout}
          >
            Log out
          </button>
        </div>
      </aside>

      <main className="main-panel">
        <header className="topbar">
          <button
            className="sidebar-toggle-btn"
            onClick={() => setSidebarOpen((prev) => !prev)}
            aria-label="Toggle Sidebar"
          >
            <svg
              viewBox="0 0 24 24"
              width="20"
              height="20"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
            >
              <path d="M3 12h18M3 6h18M3 18h18" />
            </svg>
          </button>
        </header>

        <section
          className={`conversation ${messages.length ? "has-messages" : ""}`}
        >
          {messages.length === 0 ? (
            <h2 className="welcome-title">
              What can I help you with, {userName}?
            </h2>
          ) : (
            <div className="message-list">
              {messages.map((msg, index) => (
                <article
                  className={`chat-message ${msg.role}`}
                  key={`${index}-${msg.role}`}
                >
                  {msg.role === "assistant" && (
                    <div className="assistant-mark">✳</div>
                  )}
                  <div className="message-content">{msg.content}</div>
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
          {/* PDF Attached Preview Badge */}
          {uploadedFile && (
            <div className="attached-file-badge">
              <span>📄 {uploadedFile}</span>
              <button type="button" onClick={handleRemovePdf}>
                ×
              </button>
            </div>
          )}

          <form className="composer" onSubmit={handleSend}>
            {/* Attachment Button */}
            <label className="attach-button" aria-label="Attach PDF">
              <input
                type="file"
                accept="application/pdf"
                onChange={handleFileChange}
                hidden
                disabled={loading}
              />
              <svg
                viewBox="0 0 24 24"
                width="20"
                height="20"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
              >
                <path d="M21.44 11.05l-9.19 9.19a6 6 0 01-8.49-8.49l9.19-9.19a4 4 0 015.66 5.66l-9.2 9.19a2 2 0 01-2.83-2.83l8.49-8.48" />
              </svg>
            </label>

            <textarea
              ref={inputRef}
              value={input}
              onChange={(event) => setInput(event.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Message your chatbot or attach PDF..."
              rows={1}
              disabled={loading}
            />

            <button
              className="send-button"
              type="submit"
              disabled={loading || (!input.trim() && !uploadedFile)}
            >
              {loading ? (
                <span className="send-spinner" />
              ) : (
                <svg viewBox="0 0 24 24">
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
