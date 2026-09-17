from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from collaborating_agents.message import Message
from collaborating_agents.tool import Tool


@dataclass
class LLMResponse:
    """Standardized response from an LLM call."""

    content: str
    tool_calls: Optional[List[Dict[str, Any]]] = None
    raw_response: Optional[Any] = None
    usage: Dict[str, Any] = field(default_factory=dict)


class BaseLLMClient(ABC):
    """Abstract interface for LLM backends."""

    @abstractmethod
    async def generate(
        self,
        messages: List[Message],
        tools: Optional[List[Tool]] = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Generates a response given a list of messages and optional available tools."""
        pass
