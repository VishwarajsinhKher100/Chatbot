import { useState } from "react";
import "./Auth.css";

export default function Auth({ onLoginSuccess }) {
  const [isSignUp, setIsSignUp] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setLoading(true);

    const endpoint = isSignUp
      ? "http://localhost:8000/signup"
      : "http://localhost:8000/signin";
    const payload = isSignUp ? { name, email, password } : { email, password };

    try {
      const response = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || "Authentication failed.");
      }

      const data = await response.json();

      // Pass token or user data back up to App.jsx
      onLoginSuccess(data);
    } catch (err) {
      setError(err.message || "Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-shell">
      <div className="auth-card">
        <div className="auth-header">
          <h1 className="auth-brand">Chatbot</h1>
          <h2 className="auth-title">
            {isSignUp ? "Create an account" : "Welcome back"}
          </h2>
          <p className="auth-subtitle">
            {isSignUp
              ? "Enter your details to get started."
              : "Enter your credentials to access your chats."}
          </p>
        </div>

        {error && <div className="auth-error">{error}</div>}

        <form className="auth-form" onSubmit={handleSubmit}>
          {isSignUp && (
            <div className="input-group">
              <label>Name</label>
              <input
                type="text"
                placeholder="John Doe"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                disabled={loading}
              />
            </div>
          )}

          <div className="input-group">
            <label>Email</label>
            <input
              type="email"
              placeholder="name@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              disabled={loading}
            />
          </div>

          <div className="input-group">
            <label>Password</label>
            <input
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              disabled={loading}
            />
          </div>

          <button className="auth-submit-btn" type="submit" disabled={loading}>
            {loading ? (
              <span className="send-spinner" />
            ) : isSignUp ? (
              "Sign Up"
            ) : (
              "Sign In"
            )}
          </button>
        </form>

        <div className="auth-switch">
          {isSignUp ? (
            <p>
              Already have an account?{" "}
              <button onClick={() => setIsSignUp(false)} type="button">
                Sign In
              </button>
            </p>
          ) : (
            <p>
              Don't have an account?{" "}
              <button onClick={() => setIsSignUp(true)} type="button">
                Sign Up
              </button>
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
