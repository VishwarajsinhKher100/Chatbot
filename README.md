# Multi-Turn LLM Conversation Chatbot

A ChatGPT-inspired AI chatbot that supports continuous, multi-turn conversations between a user and a Large Language Model (LLM). Built with **React, FastAPI, LangGraph, and Groq**.

The chatbot maintains conversation history using session IDs automatically managed and issued by the backend, allowing the LLM to use previous messages as context when generating responses.

## Tech Stack

- **Frontend:** React, Vite, CSS
- **Backend:** FastAPI, Python
- **LLM Orchestration:** LangGraph
- **LLM Integration:** LangChain Groq
- **Conversation State:** LangGraph `InMemorySaver`
- **LLM Provider:** Groq

## Features

- User Authentication (Sign In & Sign Up views)
- Collapsible sidebar with modern ChatGPT-inspired layout
- Sidebar-integrated **+ New chat** button and **Log out** functionality
- Multi-turn user and AI conversations
- Context-aware responses using previous messages
- Backend-managed session creation and tracking
- REST API for sending messages, receiving responses, and authentication
- Interactive message composer and conversation view
- Loading indicator while the AI generates a response
- Error handling for failed API requests
- FastAPI interactive API documentation

## Project Structure

```text
chatbot/
├── backend/
│   ├── main.py
│   ├── graph.py
│   ├── schemas.py
│   ├── routers/
│   │   ├── __init__.py
│   │   └── chat.py
│   └── .env
│
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── Auth.jsx
    │   │   └── Auth.css
    │   ├── App.jsx
    │   ├── App.css
    │   ├── index.css
    │   └── main.jsx
    ├── package.json
    └── index.html
```

## Prerequisites

Install the following before running the project:

- Python 3.10 or later
- Node.js and npm
- A Groq API key

## Installation and Setup

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd chatbot
```

Replace `<your-repository-url>` with repository URL.

### 2. Set Up the Backend

Navigate to the backend directory:

```bash
cd backend
```

Create and activate a virtual environment.

**Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**

```bash
python -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
uv sync
```

### 3. Configure Environment Variables

Create a `.env` file inside the `backend` directory:

```env
GROQ_API_KEY=your_groq_api_key
```

Replace `your_groq_api_key` with your actual API key.

**Security:** Never commit your `.env` file or expose your API key in the React frontend.

### 4. Start the Backend Server

From the `backend` directory, run:

```bash
uvicorn main:app --reload --port 8000
```

The backend will run at:

- API: http://localhost:8000
- Interactive API documentation: http://localhost:8000/docs

### 5. Set Up the Frontend

Open a new terminal and navigate to the frontend directory:

```bash
cd frontend
npm install
```

Start the React development server:

```bash
npm run dev
```

Open the application in your browser:

http://localhost:5173

## How It Works

The application follows a simple request-response architecture with local authentication state management.

```text
User / Auth State
 |
 +--> Unauthenticated --> Auth View (Sign In / Sign Up)
 |                             | (POST /signin or /signup)
 |                             v
 |                      Save Token & User Info
 |                             |
 +--> Authenticated --> Render Sidebar + Main Panel
                            |
                            | POST /chat (session_id is optional)
                            v
                    FastAPI Backend (main.py -> routers/chat.py)
                            |
                            | Generate session_id if missing/null
                            v
                    LangGraph StateGraph (graph.py)
                            |
                            | Load conversation state via thread_id
                            | Append user message
                            v
                    Groq Chat Model
                            |
                            | Generate response
                            v
                    LangGraph Checkpointer
                            |
                            v
                    FastAPI JSON Response (returns reply & session_id)
                            |
                            v
                    React Saves session_id & Displays AI Reply
```

### Conversation Flow & Session Management

1. **Authentication:** The user logs in via the `Auth` component. On successful authentication, the backend returns an access token and user information, which are stored in `localStorage`.
2. **Sidebar Navigation:** The sidebar displays user details, the **+ New chat** button, and the **Log out** button.
3. **Message Input:** The user enters a message in the main chat panel.
4. **API Request:** React sends the message and the current `session_id` (or `null` if starting a new chat) to the FastAPI backend (`/chat` endpoint).
5. **Session Generation:** If no `session_id` is provided, the backend generates a new UUID.
6. **State Retrieval & LLM:** LangGraph retrieves existing conversation state via `thread_id`, appends the message, and calls the Groq model.
7. **Response Handling:** FastAPI returns the AI reply along with the `session_id`. React updates state and displays the reply.
8. **New Chat & Logout:**
   - Clicking **"+ New chat"** in the sidebar resets the current `session_id` and active messages on the frontend.
   - Clicking **"Log out"** clears `localStorage` credentials and returns the user to the Authentication screen.

## API Reference

### Health Check

**Endpoint:** `GET /`

Checks whether the backend is running.

Example response:

```json
{
  "status": "Chatbot API is running"
}
```

### Authentication

#### User Sign Up

**Endpoint:** `POST /signup`

Request body:

```json
{
  "name": "Vishwaraj",
  "email": "user@example.com",
  "password": "yourpassword"
}
```

Example response:

```json
{
  "access_token": "mock-jwt-token-123",
  "token_type": "bearer",
  "user_name": "Vishwaraj"
}
```

#### User Sign In

**Endpoint:** `POST /signin`

Request body:

```json
{
  "email": "user@example.com",
  "password": "yourpassword"
}
```

Example response:

```json
{
  "access_token": "mock-jwt-token-123",
  "token_type": "bearer",
  "user_name": "Vishwaraj"
}
```

### Send a Chat Message

**Endpoint:** `POST /chat`

Content type: `application/json`

#### Initial Request (New Chat)

```json
{
  "session_id": null,
  "message": "Hello, my name is Vishwaraj."
}
```

Example response:

```json
{
  "session_id": "a3b1c9d4-8e2f-4a1b-9c3d-5e6f7a8b9c0d",
  "reply": "Hello Vishwaraj! Nice to meet you."
}
```

#### Follow-up Request (Continuing Conversation)

```json
{
  "session_id": "a3b1c9d4-8e2f-4a1b-9c3d-5e6f7a8b9c0d",
  "message": "What is my name?"
}
```

Example response:

```json
{
  "session_id": "a3b1c9d4-8e2f-4a1b-9c3d-5e6f7a8b9c0d",
  "reply": "Your name is Vishwaraj!"
}
```

## LangGraph Conversation State

The chatbot uses LangGraph's `MessagesState` to manage the message history.

The graph consists of:

- **State:** Stores the conversation messages.
- **Chatbot node:** Invokes the LLM and returns its response.
- **Start edge:** Routes execution to the chatbot node.
- **Checkpointer:** Stores state associated with each conversation thread (`thread_id`).

The `InMemorySaver` checkpointer is suitable for local development and demonstrations. Its state is lost when the backend process stops.

For persistent conversations, replace it with a supported database-backed LangGraph checkpointer, such as a PostgreSQL checkpointer.

## Current Scope

This project focuses on multi-turn text conversations between an authenticated user and an LLM in a sidebar-driven UI.

It does not include:

- Retrieval-Augmented Generation (RAG)
- External tools or autonomous agents
- File uploads or document processing
- Voice or image conversations
- Database-backed user account management (currently mock token implementation)
- Persistent conversation history across browser refreshes or backend restarts
- A backend API for listing or managing past conversation history

## Troubleshooting

### Groq API Key Error

- Verify that the `.env` file exists in the backend directory.
- Confirm that `GROQ_API_KEY` contains a valid key.
- Restart the backend after changing environment variables.

### Frontend Cannot Connect to Backend

- Confirm that FastAPI is running on port `8000`.
- Confirm that React is running on port `5173`.
- Check the CORS configuration in `main.py`.

### Conversation Context Is Lost

- Ensure that the `session_id` returned from the first response is being stored and included in follow-up requests.
- Avoid restarting the backend when using `InMemorySaver`.
- Use a persistent checkpointer if conversations must survive server restarts.

### Authentication Errors

- Verify that `/signup` and `/signin` routes are correctly registered on your FastAPI app.

## Future Improvements

- Persistent conversation storage (PostgreSQL / Redis checkpointer)
- Full database persistence for user credentials and hashed passwords
- Backend endpoints for saving, listing, and switching between past chat sessions in the sidebar
- Streaming LLM responses (Server-Sent Events / WebSockets)
- Deployment using Docker
- Production logging and monitoring