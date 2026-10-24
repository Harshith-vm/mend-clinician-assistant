"""
session_memory.py
=================
Lightweight conversation memory for the therapy assistant.
Stores the last N turns (user + assistant messages) and formats them
for any LLM in a standard role-based message list format.

This is LLM-agnostic. The message format is:
    [{"role": "user"|"assistant", "content": str}, ...]

Compatible with: Ollama, OpenAI, Anthropic, Gemini, LangChain, etc.
"""

import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal


Role = Literal["user", "assistant", "system"]


@dataclass
class Message:
    role: Role
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return {"role": self.role, "content": self.content}


class SessionMemory:
    """
    Maintains a rolling window of conversation turns.

    Parameters
    ----------
    max_turns : int
        Maximum number of user+assistant exchange pairs to keep.
        Older turns are dropped to stay within LLM context limits.
    session_id : str
        Unique identifier for this session.
    persist_path : str | None
        If set, saves/loads history from this JSON file path.
    """

    def __init__(self, max_turns: int = 8, session_id: str = "default",
                 persist_path: str | None = None):
        self.max_turns = max_turns
        self.session_id = session_id
        self.persist_path = persist_path
        self._history: list[Message] = []

        if persist_path and os.path.exists(persist_path):
            self._load()

    def add_user(self, text: str):
        """Record a patient message."""
        self._history.append(Message(role="user", content=text))
        self._trim()

    def add_assistant(self, text: str):
        """Record an assistant response."""
        self._history.append(Message(role="assistant", content=text))
        self._trim()

    def get_messages(self, system_prompt: str | None = None) -> list[dict]:
        """
        Returns the full message list ready for an LLM call.
        Prepends the system prompt if provided.

        Example output:
            [
                {"role": "system",    "content": "You are a compassionate..."},
                {"role": "user",      "content": "I feel so alone..."},
                {"role": "assistant", "content": "I hear you..."},
                {"role": "user",      "content": "It's been weeks..."},
            ]
        """
        msgs = []
        if system_prompt:
            msgs.append({"role": "system", "content": system_prompt})
        msgs.extend(m.to_dict() for m in self._history)
        return msgs

    def get_context_string(self) -> str:
        """
        Returns conversation history as a plain string block.
        Useful for LLMs that don't support role-based message lists.
        """
        lines = []
        for m in self._history:
            prefix = "Patient" if m.role == "user" else "Assistant"
            lines.append(f"{prefix}: {m.content}")
        return "\n".join(lines)

    def is_empty(self) -> bool:
        return len(self._history) == 0

    def clear(self):
        self._history.clear()
        if self.persist_path and os.path.exists(self.persist_path):
            os.remove(self.persist_path)

    def save(self):
        """Persist conversation history to JSON."""
        if not self.persist_path:
            return
        os.makedirs(os.path.dirname(self.persist_path), exist_ok=True)
        data = {
            "session_id": self.session_id,
            "history": [
                {"role": m.role, "content": m.content, "timestamp": m.timestamp}
                for m in self._history
            ]
        }
        with open(self.persist_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _load(self):
        with open(self.persist_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for m in data.get("history", []):
            self._history.append(
                Message(role=m["role"], content=m["content"],
                        timestamp=m.get("timestamp", ""))
            )
        self._trim()

    def _trim(self):
        """Keep only the last max_turns * 2 messages (each turn = 1 user + 1 assistant)."""
        max_msgs = self.max_turns * 2
        if len(self._history) > max_msgs:
            self._history = self._history[-max_msgs:]

    def __len__(self):
        return len(self._history)

    def __repr__(self):
        return f"<SessionMemory id={self.session_id} turns={len(self._history)//2}>"
