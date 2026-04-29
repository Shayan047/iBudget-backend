import redis
import json
import os

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=0,
    decode_responses=True,
)

SESSION_TTL = 60 * 60 * 24  # 24 hours in seconds
SESSION_KEY_PREFIX = "chat_session:"


def get_session_history(session_id: str) -> list:
    """Fetch message history for a session from Redis."""
    key = f"{SESSION_KEY_PREFIX}{session_id}"
    data = redis_client.get(key)
    return json.loads(data) if data else []


def save_session_history(session_id: str, history: list) -> None:
    """Save updated message history to Redis with TTL."""
    key = f"{SESSION_KEY_PREFIX}{session_id}"
    redis_client.setex(key, SESSION_TTL, json.dumps(history))


def clear_session_history(session_id: str) -> None:
    """Delete a session from Redis."""
    key = f"{SESSION_KEY_PREFIX}{session_id}"
    redis_client.delete(key)
