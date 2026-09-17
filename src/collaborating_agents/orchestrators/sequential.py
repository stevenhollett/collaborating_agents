from __future__ import annotations

from typing import Any, List, Optional, Union

from collaborating_agents.agent import Agent
from collaborating_agents.context import CollaborationContext, CollaborationResult
from collaborating_agents.message import Message
from collaborating_agents.orchestrators.base import BaseOrchestrator


class SequentialPipeline(BaseOrchestrator):
    """Executes a series of agents in sequence, where each agent processes the output of its predecessor."""

    def __init__(
        self,
        agents: List[Agent],
        accumulate_history: bool = True,
    ) -> None:
        super().__init__(agents)
        self.accumulate_history = accumulate_history

    async def run(
        self,
        task: Union[str, Message],
        context: Optional[CollaborationContext] = None,
        **kwargs: Any,
    ) -> CollaborationResult:
        ctx = context or CollaborationContext()
        current_msg = self._prepare_task_message(task)
        ctx.add_message(current_msg)

        for agent in self.agents:
            history = ctx.messages if self.accumulate_history else None
            output_msg = await agent.step(
                input_message=current_msg,
                context_messages=history,
            )
            ctx.add_message(output_msg)
            current_msg = output_msg

        return ctx.to_result(final_message=current_msg)
