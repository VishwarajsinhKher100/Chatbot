# Multi-Turn LLM Conversation Chatbot

A ChatGPT-inspired AI chatbot that supports continuous, multi-turn conversations between a user and a Large Language Model (LLM). Built with **React, FastAPI, LangGraph, and Groq**.

The chatbot maintains conversation history using a unique session ID, allowing the LLM to use previous messages as context when generating responses.

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
- Session-based conversation state
- REST API for sending messages and receiving responses
- ChatGPT-style UI with a modern chat layout and sidebar
- New-chat functionality
- Recents section for switching between conversations
- Interactive message composer and conversation view
- Loading indicator while the AI generates a response
- Error handling for failed API requests
- FastAPI interactive API documentation

## Project Structure

```text
chatbot/
├── backend/
│   ├── main.py
│   ├── __init__.py
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
- An Groq API key

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
 | POST /chat
 v
FastAPI Backend
 |
 v
LangGraph StateGraph
 |
 | Load conversation state
 | Append user message
 v
Groq Chat Model
 |
 | Generate response
 v
LangGraph Checkpointer
 |
 v
FastAPI JSON Response
 |
 v
React Displays AI Reply
```

### Conversation Flow

1. The user enters a message in the React chat interface.
2. React sends the message and session ID to the FastAPI backend.
3. LangGraph retrieves the existing conversation state for that session.
4. The new user message is added to the conversation.
5. The LLM generates a response using the conversation history.
6. LangGraph saves the updated state using its checkpointer.
7. FastAPI returns the response to React.
8. React displays the AI reply in the chat interface.

The same session ID is reused for subsequent messages, allowing the conversation to continue across multiple turns.

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

Request body:

```json
{
  "session_id": "session-123",
  "message": "Hello, my name is Rahul."
}
```

Example response:

```json
{
  "session_id": "session-123",
  "reply": "Hello Rahul! Nice to meet you."
}
```

Send another request with the same session ID:

```json
{
  "session_id": "session-123",
  "message": "What is my name?"
}
```

The model can answer using the previous conversation context.

Use a different session ID to start a separate conversation.

## LangGraph Conversation State

The chatbot uses LangGraph's `MessagesState` to manage the message history.

The graph consists of:

- **State:** Stores the conversation messages.
- **Chatbot node:** Invokes the LLM and returns its response.
- **Start edge:** Routes execution to the chatbot node.
- **Checkpointer:** Stores state associated with each conversation thread.

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
- Persistent conversation history across browser refreshes
- A backend API for listing or managing conversation history

Note: Recent chats are currently held in frontend state. Persistent history requires additional storage and backend support.

## Troubleshooting

### OpenAI API Key Error

- Verify that the `.env` file exists in the backend directory.
- Confirm that `GROQ_API_KEY` contains a valid key.
- Restart the backend after changing environment variables.

### Frontend Cannot Connect to Backend

- Confirm that FastAPI is running on port `8000`.
- Confirm that React is running on port `5173`.
- Check the CORS configuration in `main.py`.

### Conversation Context Is Lost

- Ensure that the same session ID is used for every message in a conversation.
- Avoid restarting the backend when using `InMemorySaver`.
- Use a persistent checkpointer if conversations must survive restarts.

### Model Errors

- Verify that the configured model is available to your OpenAI account.
- Check your API usage limits and billing configuration.

## Future Improvements

- Persistent conversation storage
- Synchronization of recent chats with the backend
- Streaming LLM responses
- User authentication
- Database-backed conversation history
- Deployment using Docker
- Production logging and monitoring
