from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, MessagesState, START
from langchain_core.messages import SystemMessage
from langgraph.checkpoint.memory import InMemorySaver
from .rag_store import retrieve_context_for_session

load_dotenv()

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
)


def chatbot(state: MessagesState, config: dict = None):
    messages = state["messages"]
    latest_user_message = messages[-1].content if messages else ""

    # Safely extract session_id from thread configuration
    session_id = ""
    if config and isinstance(config, dict):
        configurable = config.get("configurable", {})
        if configurable:
            session_id = configurable.get("thread_id", "")

    # Retrieve PDF context specific to this session
    context = (
        retrieve_context_for_session(latest_user_message, session_id)
        if session_id
        else ""
    )

    system_prompt = SystemMessage(
        content=(
            "You are a helpful AI assistant. Answer user questions based on the "
            "provided document context if available.\n\n"
            f"--- Document Context ---\n{context if context else 'No document attached.'}\n------------------------"
        )
    )

    response = llm.invoke([system_prompt] + messages)
    return {"messages": [response]}


builder = StateGraph(MessagesState)
builder.add_node("chatbot", chatbot)
builder.add_edge(START, "chatbot")

graph = builder.compile(checkpointer=InMemorySaver())
