from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ChatRequest(BaseModel):
    session_id: Optional[str] = Field(default=None, max_length=128)
    message: str = Field(min_length=1, max_length=20000)


class ChatResponse(BaseModel):
    session_id: str
    reply: str


class SignUpRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=5, max_length=255)
    password: str = Field(min_length=6, max_length=100)


class SignInRequest(BaseModel):
    email: str = Field(min_length=5, max_length=255)
    password: str = Field(min_length=6, max_length=100)


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_name: str


class SessionSummary(BaseModel):
    session_id: str
    title: str
    created_at: datetime


class MessageDetail(BaseModel):
    role: str
    content: str
    created_at: datetime


class SessionHistoryResponse(BaseModel):
    session_id: str
    messages: List[MessageDetail]
