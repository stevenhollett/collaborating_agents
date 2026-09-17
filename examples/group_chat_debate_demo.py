#!/usr/bin/env python3
"""Example demonstrating a Group Chat multi-agent debate with consensus termination."""

import asyncio
from collaborating_agents.agent import Agent
from collaborating_agents.llm.providers import MockLLMClient
from collaborating_agents.orchestrators.group_chat import GroupChat


async def main() -> None:
    print("=== Group Chat Debate Demo ===\n")

    innovator = Agent(
        name="Innovator",
        role="Creative Visionary",
        instructions="Propose ambitious and innovative ideas.",
        llm=MockLLMClient(
            responses=[
                "We should use autonomous self-healing microservices.",
                "Agreed, we will use canary deployments with automated circuit breakers.",
            ]
        ),
    )

    pragmatist = Agent(
        name="Pragmatist",
        role="Systems Reliability Engineer",
        instructions="Scrutinize proposals for failure modes and operational complexity.",
        llm=MockLLMClient(
            responses=[
                "Self-healing adds cascading failure risks without strict guardrails.",
                "TERMINATE: Canary deployments with circuit breakers satisfy both reliability and innovation.",
            ]
        ),
    )

    chat = GroupChat(
        agents=[innovator, pragmatist],
        max_rounds=5,
        speaker_selection="round_robin",
        termination_keyword="TERMINATE",
    )

    task = "Determine the architectural resilience model for high-scale deployment."
    print(f"Discussion Topic: {task}\n")

    result = await chat.run(task)

    print("Transcript:")
    for msg in result.messages:
        print(f"[{msg.sender}]: {msg.content}")

    print(f"\nConclusion:\n{result.final_text}")


if __name__ == "__main__":
    asyncio.run(main())
