"""
Simple JSON-file backed memory store for conversation history.
"""

import json
import os

MEMORY_FILE = "memory/conversations.json"


def load_memory() -> dict:
    """Load all conversation histories from disk."""
    if not os.path.exists(MEMORY_FILE):
        return {}
    with open(MEMORY_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def save_memory(data: dict) -> None:
    """Persist all conversation histories to disk."""
    os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=2)


def get_history(chat_id: str) -> list:
    """Return message history for a specific chat session."""
    memory = load_memory()
    return memory.get(chat_id, [])


def append_message(chat_id: str, role: str, content: str) -> None:
    """Append a single message to a chat session's history."""
    memory = load_memory()
    if chat_id not in memory:
        memory[chat_id] = []
    memory[chat_id].append({"role": role, "content": content})
    save_memory(memory)


def clear_history(chat_id: str) -> None:
    """Delete a chat session's history."""
    memory = load_memory()
    memory.pop(chat_id, None)
    save_memory(memory)
