from pydantic import BaseModel


class ChatPrompt(BaseModel):
    query: str
    session_id: str  # frontend-generated UUID


class ChatResponse(BaseModel):
    reply: str  # clean response for frontends
