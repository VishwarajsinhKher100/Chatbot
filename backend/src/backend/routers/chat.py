from fastapi import APIRouter, HTTPException
from langchain_core.messages import HumanMessage
from ..schemas import ChatRequest, ChatResponse
from ..graph import graph

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        result = graph.invoke(
            {"messages": [HumanMessage(content=request.message)]},
            config={"configurable": {"thread_id": request.session_id}},
        )

        reply = result["messages"][-1].content

        if not isinstance(reply, str):
            reply = str(reply)

        return ChatResponse(
            session_id=request.session_id,
            reply=reply,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to generate a response.",
        ) from exc