from typing import TypedDict, Annotated
from langchain.chat_models import init_chat_model
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
from dotenv import load_dotenv
import sqlite3

load_dotenv()

# model
model = init_chat_model("groq:llama-3.1-8b-instant")

# State
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def chat_node(state: ChatState):
   messages = state["messages"]
   response = model.invoke(messages)
   return {"messages": [response]}

conn = sqlite3.connect(database="chatbot.db", check_same_thread=False)
# Checkpointer
checkpointer = SqliteSaver(conn=conn)

# Graph
graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

chatbot = graph.compile(checkpointer=checkpointer)

def retrieve_all_threads():
    """Returns a dictionary mapping thread_id to a meaningful first-prompt label."""
    thread_labels = {}

    # Iterate over all stored checkpoints
    for checkpoint in checkpointer.list(None):
        thread_id = checkpoint.config["configurable"]["thread_id"]
    
        # Avoid re-processing if we already found a label for this thread
        if thread_id in thread_labels and thread_labels[thread_id] != f"New Conversation ({thread_id[:8]})":
            continue
            
        # Extract messages from the checkpoint state
        messages = checkpoint.metadata.get("writes", {}).get("chat_node", {}).get("messages", [])
        if not messages and "channel_values" in checkpoint.checkpoint:
            messages = checkpoint.checkpoint["channel_values"].get("messages", [])
        
        # Find the first HumanMessage to use as a meaningful title
        label = None
        for msg in messages:
            # Depending on serialization, checking the class name or type is safest
            if isinstance(msg, HumanMessage) or (has_type := getattr(msg, "type", None)) == "human":
                content = msg.content
                # Clean up and truncate the label so it fits beautifully in the sidebar
                label = content[:28] + "..." if len(content) > 28 else content
                break
        
        # Fallback if the thread exists but has no user messages yet
        thread_labels[thread_id] = label if label else f"New Conversation ({thread_id[:8]})"
        
    return thread_labels