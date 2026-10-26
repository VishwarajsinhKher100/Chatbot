import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from langchain_core.messages import HumanMessage
from ..schemas import ChatRequest, ChatResponse
from ..database import get_db
from ..models import ChatMessage, User
from ..dependencies import get_current_user
from ..graph import graph

router = APIRouter(tags=["chat"])

@router.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        session_id = request.session_id or str(uuid.uuid4())

        # 1. Save user message tied to authenticated user email
        user_msg_record = ChatMessage(
            session_id=session_id,
            user_email=current_user.email,
            role="user",
            content=request.message
        )
        db.add(user_msg_record)
        db.commit()

        # 2. Invoke LangGraph AI model
        result = graph.invoke(
            {"messages": [HumanMessage(content=request.message)]},
            config={"configurable": {"thread_id": session_id}},
        )

        reply = result["messages"][-1].content
        if not isinstance(reply, str):
            reply = str(reply)

        # 3. Save assistant response
        assistant_msg_record = ChatMessage(
            session_id=session_id,
            user_email=current_user.email,
            role="assistant",
            content=reply
        )
        db.add(assistant_msg_record)
        db.commit()

        return ChatResponse(
            session_id=session_id,
            reply=reply,
        )

    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unable to generate a response or save to database.",
        ) from exc