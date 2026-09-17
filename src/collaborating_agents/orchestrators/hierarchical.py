from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Union

from collaborating_agents.agent import Agent
from collaborating_agents.context import CollaborationContext, CollaborationResult
from collaborating_agents.message import Message, MessageRole
from collaborating_agents.orchestrators.base import BaseOrchestrator
from collaborating_agents.tool import Tool

logger = logging.getLogger(__name__)


class HierarchicalSupervisor(BaseOrchestrator):
    """Hierarchical orchestrator where a lead supervisor coordinates and delegates to specialized workers."""

    def __init__(
        self,
        supervisor: Agent,
        workers: List[Agent],
        max_delegations: int = 5,
    ) -> None:
        super().__init__(workers)
        self.supervisor = supervisor
        self.workers = workers
        self.workers_by_name: Dict[str, Agent] = {w.name: w for w in workers}
        self.max_delegations = max_delegations

        # Equip supervisor with a delegation tool
        self._register_delegation_tool()

    def _register_delegation_tool(self) -> None:
        async def delegate_to_worker(worker_name: str, subtask: str) -> str:
            """Delegates a subtask to a named worker agent and returns their response."""
            for name, worker in self.workers_by_name.items():
                if name.lower() == worker_name.strip().lower():
                    worker_msg = Message(
                        role=MessageRole.USER,
                        sender="supervisor",
                        content=subtask,
                    )
                    res = await worker.step(input_message=worker_msg)
                    return f"[{worker.name}]: {res.content}"
            return f"Error: Worker '{worker_name}' does not exist. Available workers: {list(self.workers_by_name.keys())}"

        tool = Tool(
            name="delegate_to_worker",
            description="Delegates a subtask to one of the specialized workers and receives their analysis or output.",
            func=delegate_to_worker,
            parameters_schema={
                "type": "object",
                "properties": {
                    "worker_name": {
                        "type": "string",
                        "description": f"Target worker name from: {list(self.workers_by_name.keys())}",
                    },
                    "subtask": {
                        "type": "string",
                        "description": "Specific task or question for the worker to address.",
                    },
                },
                "required": ["worker_name", "subtask"],
            },
        )
        self.supervisor.add_tool(tool)

    def _parse_text_delegation(self, text: str) -> Optional[tuple[str, str]]:
        """Parses fallback delegation commands if models output text-based directives."""
        lines = text.strip().splitlines()
        for line in lines:
            if line.upper().startswith("DELEGATE:"):
                payload = line[len("DELEGATE:") :].strip()
                if "|" in payload:
                    wname, subtask = payload.split("|", 1)
                    return wname.strip(), subtask.strip()
        return None

    async def run(
        self,
        task: Union[str, Message],
        context: Optional[CollaborationContext] = None,
        **kwargs: Any,
    ) -> CollaborationResult:
        ctx = context or CollaborationContext()
        task_msg = self._prepare_task_message(task)
        ctx.add_message(task_msg)

        workers_info = "\n".join(
            [f"- {w.name} (Role: {w.role}): {w.instructions}" for w in self.workers]
        )
        guidance = Message(
            role=MessageRole.SYSTEM,
            sender="coordinator",
            content=(
                f"You are the Supervisor. You lead a team of specialized agents:\n{workers_info}\n"
                "Break down the user's task, delegate subtasks to workers using the delegate_to_worker tool "
                "or by formatting a line like: DELEGATE: <worker_name> | <subtask>.\n"
                "When all information is gathered, synthesize and present your comprehensive final solution."
            ),
        )

        supervisor_history: List[Message] = [guidance, task_msg]
        final_msg: Optional[Message] = None

        for step_idx in range(self.max_delegations):
            response = await self.supervisor.step(context_messages=supervisor_history)
            ctx.add_message(response)
            supervisor_history.append(response)

            # Check if text-based delegation command was emitted
            delegation = self._parse_text_delegation(response.content)
            if delegation:
                wname, subtask = delegation
                matched_worker = None
                for name, w in self.workers_by_name.items():
                    if name.lower() == wname.lower():
                        matched_worker = w
                        break

                if matched_worker:
                    worker_input = Message(
                        role=MessageRole.USER,
                        sender="supervisor",
                        content=subtask,
                    )
                    worker_res = await matched_worker.step(input_message=worker_input)
                    ctx.add_message(worker_res)

                    report_back = Message(
                        role=MessageRole.TOOL,
                        sender=matched_worker.name,
                        content=f"Worker {matched_worker.name} completed subtask:\n{worker_res.content}",
                    )
                    supervisor_history.append(report_back)
                    ctx.add_message(report_back)
                    continue

            # If no tool calls were made and no delegation line was found, supervisor has concluded
            final_msg = response
            break

        if not final_msg:
            final_msg = response

        return ctx.to_result(final_message=final_msg)
