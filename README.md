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

- Multi-turn user and AI conversations
- Context-aware responses using previous messages
- Backend-managed session creation and tracking
- REST API for sending messages and receiving responses
- ChatGPT-style UI with a modern chat layout
- New-chat functionality
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

The application follows a simple request-response architecture.

```text
User
 |
 v
React Chat Interface
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

### Conversation Flow

1. The user enters a message in the React chat interface.
2. React sends the message and the current `session_id` (or `null` if starting a new chat) to the FastAPI backend (`/chat` endpoint).
3. If no `session_id` is provided, the backend generates a new UUID.
4. LangGraph retrieves the existing conversation state for that session via the checkpointer (`thread_id`).
5. The new user message is added to the conversation.
6. The LLM generates a response using the conversation history.
7. LangGraph saves the updated state using its checkpointer.
8. FastAPI returns the AI reply along with the `session_id`.
9. React saves the returned `session_id` to state and displays the AI reply in the chat interface.

Subsequent messages in the same conversation automatically send the saved `session_id`, preserving conversation context. Clicking **"+ New chat"** clears the session ID on the frontend, causing the next message to trigger a new session on the backend.

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

### Send a Chat Message

**Endpoint:** `POST /chat`

Content type: `application/json`

#### Initial Request (New Chat)

Sending a request without a `session_id` (or with `null`) creates a new chat session:

```json
{
  "session_id": null,
  "message": "Hello, my name is Vishwaraj."
}
```

Example response (returns the generated `session_id`):

```json
{
  "session_id": "a3b1c9d4-8e2f-4a1b-9c3d-5e6f7a8b9c0d",
  "reply": "Hello Vishwaraj! Nice to meet you."
}
```

#### Follow-up Request (Continuing Conversation)

Send subsequent requests using the returned `session_id` to maintain context:

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

This project focuses on multi-turn text conversations between a user and an LLM, presented in a ChatGPT-inspired interface.

It does not include:

- Retrieval-Augmented Generation (RAG)
- External tools or autonomous agents
- File uploads or document processing
- Voice or image conversations
- User authentication
- Persistent conversation history across browser refreshes or backend restarts
- A backend API for listing or managing conversation history

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

### Model Errors

- Verify that the configured model is available on your Groq account.
- Check your API usage limits and billing configuration.

## Future Improvements

- Persistent conversation storage (PostgreSQL / Redis checkpointer)
- Backend endpoints for saving, listing, and switching between past chat sessions
- Streaming LLM responses (Server-Sent Events / WebSockets)
- User authentication
- Deployment using Docker
- Production logging and monitoring