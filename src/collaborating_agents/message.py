from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class MessageRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"
    COORDINATOR = "coordinator"


@dataclass
class Message:
    """Represents a discrete communication unit exchanged between agents or orchestrators."""

    content: str
    role: MessageRole = MessageRole.USER
    sender: str = "user"
    recipient: Optional[str] = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    tool_calls: Optional[List[Dict[str, Any]]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "role": self.role.value if isinstance(self.role, MessageRole) else str(self.role),
            "sender": self.sender,
            "recipient": self.recipient,
            "content": self.content,
            "tool_calls": self.tool_calls,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Message:
        role = data.get("role", MessageRole.USER)
        if isinstance(role, str):
            try:
                role = MessageRole(role)
            except ValueError:
                pass
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            role=role,
            sender=data.get("sender", "user"),
            recipient=data.get("recipient"),
            content=data.get("content", ""),
            tool_calls=data.get("tool_calls"),
            metadata=data.get("metadata", {}),
            timestamp=data.get("timestamp", time.time()),
        )
