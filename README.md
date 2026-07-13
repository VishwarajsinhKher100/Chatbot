# Conversational Chatbot

An advanced conversational AI assistant that remembers past interactions and leverages integrated tools to accomplish complex tasks. Similar to ChatGPT, it maintains continuous context for natural, multi-turn dialogue while seamlessly executing external functions to deliver dynamic, action-oriented responses.

# Features

* ChatGPT-Style Interface: A clean, intuitive frontend designed for seamless, multi-turn natural language interactions.

* Real-Time Streaming: Responses stream back to the UI token-by-token as they are generated, ensuring a fast, responsive user experience without long loading times.

* Session Persistence & Resume: Chat history is continuously saved. Users can exit the application, return later, and pick up past conversations exactly where they left off with full context intact.

* Integrated Action Tools: The bot extends beyond standard text generation by intelligently calling external functions when needed:

    * Web Search: Fetches up-to-date information from the internet.

    * Live Weather: Retrieves current conditions and forecasts for any location.

    * Stock Tracker: Pulls real-time market prices.

    * Calculator: Performs precise mathematical operations directly within the chat.

* SQLite Storage: Uses a lightweight, zero-configuration SQLite database to reliably manage user sessions, messages, and state.

* Observability & Tracing: Built-in logging and monitoring capabilities to trace tool executions, track latency, and easily debug conversation routing.

# Tech Stack

Core Language & UI

* Python: The primary programming language used for the backend logic and tool execution.

* Streamlit: Powers the ChatGPT-like frontend, enabling a responsive, real-time chat interface without writing complex HTML/CSS.

AI & Orchestration

* LangChain: The core framework used to connect the LLM with external tools (Search, Weather, Calculator, etc.) and manage prompt templates.

* LangGraph: Handles the complex state management, routing, and streaming, allowing the application to pause, resume, and track conversational memory across multiple turns.

Database & State Management

* SQLite: A lightweight, local database used to persistently store chat histories and session data.

* UUID: Generates unique session identifiers to separate and resume distinct chat threads.

Utilities & Integrations

* Requests: Handles external HTTP API calls to fetch live data (e.g., stock prices, weather).

* Dotenv: Securely loads environment variables and API keys from a .env file.

* Typing: Enforces strict Python type hints, improving code readability, maintainability, and debugging.