import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from langchain_core.messages import HumanMessage
from ..schemas import (
    ChatRequest,
    ChatResponse,
    SessionSummary,
    SessionHistoryResponse,
    MessageDetail,
)
from ..database import get_db
from ..models import ChatMessage, User
from ..dependencies import get_current_user
from ..graph import graph

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        session_id = request.session_id or str(uuid.uuid4())

        # 1. Save user message tied to authenticated user email
        user_msg_record = ChatMessage(
            session_id=session_id,
            user_email=current_user.email,
            role="user",
            content=request.message,
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
            content=reply,
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


@router.get("/sessions", response_model=list[SessionSummary])
def get_user_sessions(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    # Query distinct session_ids and get the first message content as the title & creation time
    subq = (
        db.query(
            ChatMessage.session_id,
            func.min(ChatMessage.created_at).label("first_created"),
            func.min(ChatMessage.content).label("first_content"),
        )
        .filter(ChatMessage.user_email == current_user.email)
        .group_by(ChatMessage.session_id)
        .order_by(func.min(ChatMessage.created_at).desc())
        .all()
    )

    sessions = []
    for row in subq:
        sessions.append(
            SessionSummary(
                session_id=row.session_id,
                title=(
                    row.first_content[:30] + "..."
                    if len(row.first_content) > 30
                    else row.first_content
                ),
                created_at=row.first_created,
            )
        )
    return sessions


@router.get("/sessions/{session_id}", response_model=SessionHistoryResponse)
def get_session_messages(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    messages = (
        db.query(ChatMessage)
        .filter(
            ChatMessage.session_id == session_id,
            ChatMessage.user_email == current_user.email,
        )
        .order_by(ChatMessage.created_at.asc())
        .all()
    )

    if not messages:
        raise HTTPException(status_code=404, detail="Session not found.")

    return SessionHistoryResponse(
        session_id=session_id,
        messages=[
            MessageDetail(role=msg.role, content=msg.content, created_at=msg.created_at)
            for msg in messages
        ],
    )
