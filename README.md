# Multi-Turn LLM Conversation Chatbot

A ChatGPT-inspired AI chatbot that supports continuous, multi-turn conversations between a user and a Large Language Model (LLM). Built with **React, FastAPI, LangGraph, Groq, and PostgreSQL**.

The chatbot maintains conversation history and user credentials using a persistent PostgreSQL database, allowing users to sign up securely, log in, and persist their chat interactions.

## Tech Stack

- **Frontend:** React, Vite, CSS
- **Backend:** FastAPI, Python
- **Database & ORM:** PostgreSQL, SQLAlchemy
- **LLM Orchestration:** LangGraph
- **LLM Integration:** LangChain Groq
- **LLM Provider:** Groq

## Features

- User Authentication with secure password hashing (Sign In & Sign Up)
- Persistent PostgreSQL backend storage for user accounts and chat messages
- Collapsible sidebar with modern ChatGPT-inspired layout
- Sidebar-integrated **+ New chat** button and **Log out** functionality
- Multi-turn user and AI conversations
- Context-aware responses using previous messages
- Backend-managed session creation and tracking
- REST API for sending messages, receiving responses, and authentication
- Interactive message composer and conversation view
- Loading indicator while the AI generates a response
- Error handling for failed API requests and database constraints
- FastAPI interactive API documentation

## Project Structure

```text
chatbot/
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── auth_utils.py
│   ├── graph.py
│   ├── schemas.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py
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
- PostgreSQL installed and running locally or via a cloud provider
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

### 3. Set Up PostgreSQL Database

1. Open your terminal or pgAdmin and create the PostgreSQL database:

```SQL
CREATE DATABASE chatbot_db;
```

2. Note your database credentials (username, password, host, port, and database name).

### 4. Configure Environment Variables

Create a `.env` file inside the `backend` directory:

```env
GROQ_API_KEY=your_groq_api_key
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/chatbot_db
```

Replace `your_groq_api_key` and `your_password` with your actual credentials. (Note: If your password contains special characters like @, make sure to URL encode them, e.g., `%40`).

**Security:** Never commit your `.env` file or expose your API key in the React frontend.

### 5. Start the Backend Server

From the `backend` directory, run:

```bash
uvicorn main:app --reload --port 8000
```

The application will automatically create the users and chat_messages tables in your PostgreSQL database upon startup.

The backend will run at:

- API: http://localhost:8000
- Interactive API documentation: http://localhost:8000/docs

### 6. Set Up the Frontend

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

The application follows a persistent request-response architecture backed by PostgreSQL and SQLAlchemy.

```text
User / Auth State
 |
 +--> Unauthenticated --> Auth View (Sign In / Sign Up)
 |                             | (POST /signin or /signup)
 |                             v
 |                      Validate against PostgreSQL & Return Token
 |                             |
 +--> Authenticated --> Render Sidebar + Main Panel
                            |
                            | POST /chat (session_id is optional)
                            v
                    FastAPI Backend (main.py -> routers/chat.py)
                            |
                            | Save User Message to PostgreSQL
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
                    Save Assistant Reply to PostgreSQL
                            |
                            v
                    FastAPI JSON Response (returns reply & session_id)
                            |
                            v
                    React Saves session_id & Displays AI Reply
```

### Conversation Flow & Session Management

1. **Authentication:** The user registers or signs in via the `Auth` component. Credentials are validated against the PostgreSQL `users` table with secure password hashing.
2. **Sidebar Navigation:** The sidebar displays user details, the **+ New chat** button, and the **Log out** button.
3. **Message Input:** The user enters a message in the main chat panel.
4. **API Request:** React sends the message and the current `session_id` to the FastAPI backend (`/chat` endpoint).
5. **Database Logging**: Both the incoming user prompt and the resulting AI response are persisted in the PostgreSQL `chat_messages` table tied to the session and user.
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
  "access_token": "mock-jwt-token-1",
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
  "access_token": "mock-jwt-token-1",
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

## Troubleshooting

### PostgreSQL Connection Errors

- Verify that your PostgreSQL service is running.
- Check that your DATABASE_URL string in `.env` is formatted correctly: `postgresql://username:password@localhost:5432/chatbot_db`.
- Ensure special characters in database passwords are URL-encoded.

### Groq API Key Error

- Verify that the `.env` file exists in the backend directory.
- Confirm that `GROQ_API_KEY` contains a valid key.
- Restart the backend after changing environment variables.

### Frontend Cannot Connect to Backend

- Confirm that FastAPI is running on port `8000`.
- Confirm that React is running on port `5173`.
- Check the CORS configuration in `main.py`.

### Authentication Errors

- Verify that `/signup` and `/signin` routes are correctly registered and included via `app.include_router(auth.router)`.

## Future Improvements

- Backend endpoints for listing, viewing, and switching between historical chat sessions in the sidebar
- Full JWT token generation and validation middleware
- Streaming LLM responses (Server-Sent Events / WebSockets)
- Deployment using Docker
- Production logging and monitoring
