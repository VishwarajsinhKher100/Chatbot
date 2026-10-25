import uuid
from fastapi import APIRouter, HTTPException
from langchain_core.messages import HumanMessage
from ..schemas import ChatRequest, ChatResponse
from ..graph import graph
from ..schemas import SignUpRequest, SignInRequest, AuthResponse

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        # Generate session_id on the backend if not provided
        session_id = request.session_id
        if not session_id:
            session_id = str(uuid.uuid4())

        result = graph.invoke(
            {"messages": [HumanMessage(content=request.message)]},
            config={"configurable": {"thread_id": session_id}},
        )

        reply = result["messages"][-1].content

        if not isinstance(reply, str):
            reply = str(reply)

        return ChatResponse(
            session_id=session_id,
            reply=reply,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to generate a response.",
        ) from exc


@router.post("/signup", response_model=AuthResponse)
def signup(request: SignUpRequest):
    # TODO: Add database logic to hash password and save user
    return AuthResponse(access_token="mock-jwt-token-123", user_name=request.name)


@router.post("/signin", response_model=AuthResponse)
def signin(request: SignInRequest):
    # TODO: Add database check to verify credentials
    return AuthResponse(access_token="mock-jwt-token-123", user_name="User")
