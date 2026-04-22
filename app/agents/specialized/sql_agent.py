import os
from functools import lru_cache
from langchain_community.agent_toolkits import create_sql_agent
from langchain_groq import ChatGroq
from app.database import get_langchain_db
from app.agents.prompts import SQL_AGENT_SYSTEM_PROMPT
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


@lru_cache(maxsize=1)
def get_sql_agent():
    """
    Build and cache the SQL agent.
    lru_cache ensures this runs once — not on every request.
    """
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError("GROQ_API_KEY environment variable not set")

    llm = ChatGroq(
        temperature=0,
        model_name="llama-3.3-70b-versatile",
        groq_api_key=groq_api_key,
    )

    db = get_langchain_db()

    agent_prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", SQL_AGENT_SYSTEM_PROMPT),  # Your rules and context
            ("human", "{input}"),  # Where the user's actual question goes
            MessagesPlaceholder(
                variable_name="agent_scratchpad"
            ),  # The required space for the agent to "think"
        ]
    )

    return create_sql_agent(
        llm=llm,
        db=db,
        prompt=agent_prompt_template,
        agent_type="openai-tools",
        verbose=True,
    )
