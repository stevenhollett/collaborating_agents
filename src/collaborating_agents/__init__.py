"""collaborating_agents - A flexible multi-topology Python framework for collaborating autonomous agents."""

__version__ = "0.2.0"

from collaborating_agents.agent import Agent
from collaborating_agents.context import CollaborationContext, CollaborationResult
from collaborating_agents.llm.base import BaseLLMClient, LLMResponse
from collaborating_agents.llm.providers import (
    CallableLLMClient,
    GeminiLLMClient,
    MockLLMClient,
)
from collaborating_agents.message import Message, MessageRole
from collaborating_agents.orchestrators.base import BaseOrchestrator
from collaborating_agents.orchestrators.group_chat import GroupChat
from collaborating_agents.orchestrators.hierarchical import HierarchicalSupervisor
from collaborating_agents.orchestrators.sequential import SequentialPipeline
from collaborating_agents.tool import Tool, tool

__all__ = [
    "__version__",
    "Agent",
    "BaseLLMClient",
    "LLMResponse",
    "MockLLMClient",
    "CallableLLMClient",
    "GeminiLLMClient",
    "Message",
    "MessageRole",
    "Tool",
    "tool",
    "CollaborationContext",
    "CollaborationResult",
    "BaseOrchestrator",
    "SequentialPipeline",
    "GroupChat",
    "HierarchicalSupervisor",
]
