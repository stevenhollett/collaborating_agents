from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from collaborating_agents.message import Message


@dataclass
class CollaborationResult:
    """The result returned after executing an orchestrator workflow."""

    final_message: Optional[Message]
    messages: List[Message] = field(default_factory=list)
    state: Dict[str, Any] = field(default_factory=dict)
    duration_seconds: float = 0.0
    successful: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def final_text(self) -> str:
        return self.final_message.content if self.final_message else ""


class CollaborationContext:
    """Maintains shared state, execution history, and event hooks across an agent team."""

    def __init__(
        self,
        initial_state: Optional[Dict[str, Any]] = None,
        on_message: Optional[Callable[[Message], None]] = None,
    ) -> None:
        self.state: Dict[str, Any] = initial_state or {}
        self.messages: List[Message] = []
        self._on_message = on_message
        self.start_time: float = time.time()

    def add_message(self, message: Message) -> None:
        """Records a message in shared history and triggers registered listeners."""
        self.messages.append(message)
        if self._on_message:
            self._on_message(message)

    def set(self, key: str, value: Any) -> None:
        """Updates a key in the shared state."""
        self.state[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieves a key from the shared state."""
        return self.state.get(key, default)

    def to_result(
        self,
        final_message: Optional[Message],
        successful: bool = True,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> CollaborationResult:
        """Creates a CollaborationResult from the current context state."""
        return CollaborationResult(
            final_message=final_message,
            messages=list(self.messages),
            state=dict(self.state),
            duration_seconds=time.time() - self.start_time,
            successful=successful,
            metadata=metadata or {},
        )
