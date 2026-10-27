from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()

# Initialize LLM
llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
)


def chatbot(state: MessagesState):
    response = llm.invoke(state["messages"])
    return {"messages": [response]}


# Build LangGraph workflow
builder = StateGraph(MessagesState)
builder.add_node("chatbot", chatbot)
builder.add_edge(START, "chatbot")

# Compile graph with memory checkpointer
graph = builder.compile(checkpointer=InMemorySaver())
