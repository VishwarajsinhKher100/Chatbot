import streamlit as st
from langgraph_backend import chatbot, retrieve_all_threads
from langchain_core.messages import HumanMessage, AIMessage
import uuid

# ***************************************** Utility functions *************************************

def generate_thread_id():
    return str(uuid.uuid4())

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state["thread_id"] = thread_id
    add_thread(thread_id, label="New Conversation")
    st.session_state["message_history"] = []

def add_thread(thread_id, label=None):
    if "chat_threads" not in st.session_state:
        st.session_state["chat_threads"] = {}
    if thread_id not in st.session_state["chat_threads"]:
        st.session_state["chat_threads"][thread_id] = label or f"Chat {thread_id[:8]}"

def load_conversation(thread_id):
    state = chatbot.get_state(config={"configurable": {"thread_id": thread_id}})
    return state.values.get("messages", [])

# ****************************************** Session Setup *****************************************
if "message_history" not in st.session_state:
    st.session_state["message_history"] = []

if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = generate_thread_id()

# Load threads as a dictionary from SQLite backend
if "chat_threads" not in st.session_state:
    st.session_state["chat_threads"] = retrieve_all_threads()

# Ensure current thread tracker exists
add_thread(st.session_state["thread_id"], label="New Conversation")

# ***************************************** Sidebar UI *********************************************

st.sidebar.title("Chatbot")

if st.sidebar.button("New Chat"):
    reset_chat()
    st.rerun()

st.sidebar.header("My Conversations")

# Render active and past threads with their meaningful titles
for thread_id, label in list(st.session_state["chat_threads"].items())[::-1]:
    # Highlight the active thread
    button_prefix = "● " if thread_id == st.session_state["thread_id"] else "○ "
    
    if st.sidebar.button(f"{button_prefix}{label}", key=thread_id):
        st.session_state["thread_id"] = thread_id
        messages = load_conversation(thread_id)

        temp_messages = []
        for message in messages:
            role = "user" if message.type == "human" or isinstance(message, HumanMessage) else "assistant"
            temp_messages.append({"role": role, "content": message.content})
        
        st.session_state["message_history"] = temp_messages
        st.rerun() # Force instant UI update to display selected chat logs

# ****************************************** Main UI ***********************************************

# Display loaded history
for message in st.session_state["message_history"]:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# User interaction
user_input = st.chat_input("Type here")

if user_input:
    # If this is the very first message in a brand new chat, dynamically update its sidebar label
    if len(st.session_state["message_history"]) == 0:
        short_label = user_input[:28] + "..." if len(user_input) > 28 else user_input
        st.session_state["chat_threads"][st.session_state["thread_id"]] = short_label

    # Save and display user message
    st.session_state["message_history"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    CONFIG = {"configurable": {"thread_id": st.session_state["thread_id"]}}
    
    # Stream response
    with st.chat_message("assistant"):
        ai_message = st.write_stream(
            message_chunk.content for message_chunk, metadata in chatbot.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode="messages"
            )
        )
    
    st.session_state["message_history"].append({"role": "assistant", "content": ai_message})
    st.rerun()