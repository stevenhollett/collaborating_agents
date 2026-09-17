from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, List, Optional, Union

from collaborating_agents.agent import Agent
from collaborating_agents.context import CollaborationContext, CollaborationResult
from collaborating_agents.message import Message, MessageRole


class BaseOrchestrator(ABC):
    """Abstract base class for multi-agent collaboration topologies."""

    def __init__(self, agents: List[Agent]) -> None:
        self.agents = agents
        self.agents_by_name = {agent.name: agent for agent in agents}

    def _prepare_task_message(self, task: Union[str, Message]) -> Message:
        if isinstance(task, Message):
            return task
        return Message(
            role=MessageRole.USER,
            sender="user",
            content=str(task),
        )

    @abstractmethod
    async def run(
        self,
        task: Union[str, Message],
        context: Optional[CollaborationContext] = None,
        **kwargs: Any,
    ) -> CollaborationResult:
        """Executes the multi-agent collaboration topology on a given task."""
        pass
