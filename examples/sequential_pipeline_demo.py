#!/usr/bin/env python3
"""Example demonstrating a Sequential Pipeline collaboration pattern."""

import asyncio
from collaborating_agents.agent import Agent
from collaborating_agents.llm.providers import MockLLMClient
from collaborating_agents.orchestrators.sequential import SequentialPipeline


async def main() -> None:
    print("=== Sequential Pipeline Demo ===\n")

    researcher = Agent(
        name="Researcher",
        role="Information Gatherer",
        instructions="Gather key facts and raw details about the topic.",
        llm=MockLLMClient(
            default_response="Key fact: Multi-agent systems achieve higher accuracy through specialization."
        ),
    )

    analyst = Agent(
        name="Analyst",
        role="Strategist",
        instructions="Analyze the raw findings and formulate actionable recommendations.",
        llm=MockLLMClient(
            default_response="Recommendation: Implement decoupled communication bus with structured messages."
        ),
    )

    summarizer = Agent(
        name="Summarizer",
        role="Executive Editor",
        instructions="Synthesize all prior outputs into a concise executive brief.",
        llm=MockLLMClient(
            default_response="Executive Brief: Deploy specialized modular agents over a unified message bus."
        ),
    )

    pipeline = SequentialPipeline(agents=[researcher, analyst, summarizer])
    task = "Design an enterprise multi-agent architecture."
    print(f"Initial Task: {task}\n")

    result = await pipeline.run(task)

    print("Execution History:")
    for msg in result.messages:
        print(f"[{msg.sender}] ({msg.role.value}): {msg.content}")

    print(f"\nFinal Result:\n{result.final_text}")


if __name__ == "__main__":
    asyncio.run(main())
