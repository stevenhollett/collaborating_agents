from __future__ import annotations

import logging
from typing import Any, Callable, List, Optional, Union

from collaborating_agents.agent import Agent
from collaborating_agents.context import CollaborationContext, CollaborationResult
from collaborating_agents.message import Message, MessageRole
from collaborating_agents.orchestrators.base import BaseOrchestrator

logger = logging.getLogger(__name__)


class GroupChat(BaseOrchestrator):
    """Orchestrates collaborative dialogue between multiple agents in a shared room."""

    def __init__(
        self,
        agents: List[Agent],
        max_rounds: int = 10,
        speaker_selection: str = "round_robin",
        moderator: Optional[Agent] = None,
        custom_speaker_selector: Optional[
            Callable[[List[Message], List[Agent]], Agent]
        ] = None,
        termination_keyword: Optional[str] = "TERMINATE",
        termination_fn: Optional[Callable[[Message], bool]] = None,
    ) -> None:
        super().__init__(agents)
        self.max_rounds = max_rounds
        self.speaker_selection = speaker_selection
        self.moderator = moderator
        self.custom_speaker_selector = custom_speaker_selector
        self.termination_keyword = termination_keyword
        self.termination_fn = termination_fn

    async def _select_next_speaker(
        self,
        round_idx: int,
        messages: List[Message],
    ) -> Agent:
        if self.custom_speaker_selector:
            return self.custom_speaker_selector(messages, self.agents)

        if self.speaker_selection == "round_robin":
            return self.agents[round_idx % len(self.agents)]

        if self.speaker_selection == "moderator" and self.moderator:
            prompt = (
                "Given the ongoing conversation, select which agent should speak next.\n"
                f"Candidate agents: {[a.name for a in self.agents]}\n"
                "Respond ONLY with the exact name of the selected agent."
            )
            mod_msg = await self.moderator.step(
                input_message=Message(
                    role=MessageRole.USER,
                    sender="system",
                    content=prompt,
                ),
                context_messages=messages,
            )
            selected_name = mod_msg.content.strip()
            for agent in self.agents:
                if agent.name.lower() in selected_name.lower():
                    return agent
            return self.agents[round_idx % len(self.agents)]

        return self.agents[round_idx % len(self.agents)]

    def _is_terminal(self, message: Message) -> bool:
        if self.termination_fn and self.termination_fn(message):
            return True
        if self.termination_keyword and self.termination_keyword in message.content:
            return True
        return False

    async def run(
        self,
        task: Union[str, Message],
        context: Optional[CollaborationContext] = None,
        **kwargs: Any,
    ) -> CollaborationResult:
        ctx = context or CollaborationContext()
        task_msg = self._prepare_task_message(task)
        ctx.add_message(task_msg)

        last_message: Optional[Message] = task_msg

        for round_idx in range(self.max_rounds):
            speaker = await self._select_next_speaker(round_idx, ctx.messages)

            # Pass full shared conversation to the selected speaker
            response = await speaker.step(
                input_message=last_message,
                context_messages=ctx.messages,
            )
            ctx.add_message(response)
            last_message = response

            if self._is_terminal(response):
                logger.info("Termination condition satisfied at round %d", round_idx)
                break

        return ctx.to_result(final_message=last_message)
