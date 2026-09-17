from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from collaborating_agents.llm.base import BaseLLMClient
from collaborating_agents.llm.providers import MockLLMClient
from collaborating_agents.message import Message, MessageRole
from collaborating_agents.tool import Tool

logger = logging.getLogger(__name__)


@dataclass
class Agent:
    """An autonomous agent capable of reasoning, utilizing tools, and collaborating with peers."""

    name: str
    instructions: str = "You are a helpful assistant."
    role: str = "assistant"
    llm: BaseLLMClient = field(default_factory=lambda: MockLLMClient())
    tools: Dict[str, Tool] = field(default_factory=dict)
    memory: List[Message] = field(default_factory=list)
    max_tool_iterations: int = 5

    def add_tool(self, tool: Tool) -> Agent:
        """Registers a tool with the agent."""
        self.tools[tool.name] = tool
        return self

    def reset_memory(self) -> None:
        """Clears the agent's short-term message memory."""
        self.memory.clear()

    async def step(
        self,
        input_message: Optional[Message] = None,
        context_messages: Optional[List[Message]] = None,
    ) -> Message:
        """Executes a single reasoning/action step by the agent."""
        # Assemble message trajectory
        conversation: List[Message] = [
            Message(
                role=MessageRole.SYSTEM,
                sender="system",
                content=f"{self.instructions}\nYour role: {self.role}\nYour name: {self.name}",
            )
        ]

        if context_messages:
            conversation.extend(context_messages)
        else:
            conversation.extend(self.memory)

        if input_message:
            conversation.append(input_message)
            self.memory.append(input_message)

        tool_list = list(self.tools.values()) if self.tools else None
        iterations = 0

        while iterations < self.max_tool_iterations:
            iterations += 1
            response = await self.llm.generate(conversation, tools=tool_list)

            # If tool calls are requested
            if response.tool_calls:
                assistant_msg = Message(
                    role=MessageRole.ASSISTANT,
                    sender=self.name,
                    content=response.content or "",
                    tool_calls=response.tool_calls,
                )
                conversation.append(assistant_msg)
                self.memory.append(assistant_msg)

                for call in response.tool_calls:
                    call_name = call.get("name")
                    args = call.get("arguments", {})
                    if isinstance(args, str):
                        try:
                            args = json.loads(args)
                        except Exception:
                            args = {}

                    if call_name in self.tools:
                        try:
                            result = await self.tools[call_name].execute_async(**args)
                            tool_output = (
                                json.dumps(result)
                                if not isinstance(result, str)
                                else result
                            )
                        except Exception as e:
                            tool_output = f"Error executing tool '{call_name}': {str(e)}"
                    else:
                        tool_output = f"Tool '{call_name}' not found."

                    tool_msg = Message(
                        role=MessageRole.TOOL,
                        sender=call_name or "tool",
                        content=str(tool_output),
                        metadata={"tool_call_id": call.get("id")},
                    )
                    conversation.append(tool_msg)
                    self.memory.append(tool_msg)
            else:
                final_msg = Message(
                    role=MessageRole.ASSISTANT,
                    sender=self.name,
                    content=response.content,
                )
                self.memory.append(final_msg)
                return final_msg

        # Exceeded tool iterations limit
        fallback_msg = Message(
            role=MessageRole.ASSISTANT,
            sender=self.name,
            content="Max tool iterations reached without concluding.",
        )
        self.memory.append(fallback_msg)
        return fallback_msg
