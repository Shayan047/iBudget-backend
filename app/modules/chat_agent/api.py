from fastapi import APIRouter, Depends
from .schema import ChatPrompt, ChatResponse
from .service import ChatAgentService
from app.dependencies import get_current_user
from app.models import User

router = APIRouter(prefix="/budgetbot", tags=["BudgetBot"])


@router.post("/chat", response_model=ChatResponse)
def talk_to_agent(
    data: ChatPrompt,
    current_user: User = Depends(get_current_user),
):
    return ChatAgentService.chat_with_agent(data, current_user)
