# app/modules/chat_agent/service.py

from app.agents.specialized.sql_agent import get_sql_agent
from app.agents.knowledge.retriever import get_relevant_context
from app.models import User
from app.redis_client import get_session_history, save_session_history
from .schema import ChatPrompt, ChatResponse


class ChatAgentService:

    @staticmethod
    def chat_with_agent(data: ChatPrompt, current_user: User) -> ChatResponse:
        # Step 1 — Fetch conversation history from Redis
        history = get_session_history(data.session_id)

        print(f"History for session {data.session_id}")

        # Step 2 — Build history string
        history_context = ""
        if history:
            history_context = "\n".join(
                [f"{msg['role'].upper()}: {msg['content']}" for msg in history]
            )

        # Step 3 — Retrieve relevant business knowledge from vector DB
        rag_context = get_relevant_context(data.query)

        print(
            {
                "input": data.query,
                "history": history_context,
                "user_id": current_user.id,
                "rag_context": rag_context,
            }
        )

        # Step 4 — Invoke agent with all context
        agent = get_sql_agent()
        result = agent.invoke(
            {
                "input": data.query,
                "history": history_context,
                "user_id": current_user.id,
                "rag_context": rag_context,
            }
        )
        reply = result.get("output", "Sorry, I could not process your request.")

        # Step 5 — Save updated history to Redis
        history.append({"role": "user", "content": data.query})
        history.append({"role": "assistant", "content": reply})
        save_session_history(data.session_id, history)

        return ChatResponse(reply=reply)
