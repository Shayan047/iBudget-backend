from app.agents.specialized.sql_agent import get_sql_agent
from app.models import User
from app.redis_cleint import get_session_history, save_session_history
from .schema import ChatPrompt, ChatResponse
from app.agents.prompts import SQL_AGENT_SECURITY_PROMPT, SQL_AGENT_PROMPT_RULES


class ChatAgentService:

    @staticmethod
    def chat_with_agent(data: ChatPrompt, current_user: User) -> ChatResponse:
        # Step 1 — Fetch history from Redis
        history = get_session_history(data.session_id)

        # Step 2 — Build context string from history for the agent
        history_context = ""
        if history:
            history_context = "\n".join(
                [f"{msg['role'].upper()}: {msg['content']}" for msg in history]
            )

        # Step 4 — Invoke the agent
        agent = get_sql_agent()
        result = agent.invoke(
            {
                "input": data.query,
                "history": history_context,
                "user_id": current_user.id,
            }
        )
        reply = result.get("output", "Sorry, I could not process your request.")

        # Step 5 — Update history in Redis
        history.append({"role": "user", "content": data.query})
        history.append({"role": "assistant", "content": reply})
        save_session_history(data.session_id, history)

        return ChatResponse(reply=reply)
