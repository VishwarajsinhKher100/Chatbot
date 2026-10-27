const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function request(endpoint, options = {}) {
  const token = localStorage.getItem("token");

  const headers = {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorMessage = `Request failed with status ${response.status}`;
    try {
      const errorData = await response.json();
      errorMessage = errorData.detail || errorMessage;
    } catch {}
    throw new Error(errorMessage);
  }

  return response.json();
}

export const authApi = {
  signin: (credentials) =>
    request("/signin", { method: "POST", body: JSON.stringify(credentials) }),
  signup: (userData) =>
    request("/signup", { method: "POST", body: JSON.stringify(userData) }),
};

export const chatApi = {
  sendMessage: (payload) =>
    request("/chat", { method: "POST", body: JSON.stringify(payload) }),
  getSessions: () => request("/sessions", { method: "GET" }),
  getSessionHistory: (sessionId) =>
    request(`/sessions/${sessionId}`, { method: "GET" }),
};

// Add ragApi export here
export const ragApi = {
  uploadPdf: async (file, sessionId) => {
    const formData = new FormData();
    formData.append("file", file);
    if (sessionId) formData.append("session_id", sessionId);

    const token = localStorage.getItem("token");
    const response = await fetch(`${API_BASE_URL}/upload-pdf`, {
      method: "POST",
      headers: { ...(token ? { Authorization: `Bearer ${token}` } : {}) },
      body: formData,
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.detail || "Failed to upload PDF");
    }
    return response.json();
  },
  deleteSessionDocs: (sessionId) =>
    request(`/session-docs/${sessionId}`, { method: "DELETE" }),
};
