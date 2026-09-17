#!/usr/bin/env python3
"""Example demonstrating a Hierarchical Supervisor delegating tasks to specialized workers."""

import asyncio
from collaborating_agents.agent import Agent
from collaborating_agents.llm.providers import MockLLMClient
from collaborating_agents.orchestrators.hierarchical import HierarchicalSupervisor
from collaborating_agents.tool import tool


async def main() -> None:
    print("=== Hierarchical Supervisor Delegation Demo ===\n")

    @tool(name="multiply", description="Multiplies two numbers")
    def multiply(a: int, b: int) -> int:
        return a * b

    calc_client = MockLLMClient(
        responses=["Computing product...", "Result is 8400."],
        tool_call_sequence=[
            [{"id": "c1", "name": "multiply", "arguments": {"a": 70, "b": 120}}]
        ],
    )
    math_worker = Agent(
        name="Calculator",
        role="Mathematical Specialist",
        instructions="Perform accurate calculations using tools.",
        llm=calc_client,
    )
    math_worker.add_tool(multiply)

    research_worker = Agent(
        name="MarketAnalyst",
        role="Industry Expert",
        instructions="Provide industry benchmark data.",
        llm=MockLLMClient(default_response="Industry average conversion rate is 3.5%."),
    )

    supervisor_llm = MockLLMClient(
        responses=[
            "DELEGATE: Calculator | Calculate product for 70 units at 120 dollars each",
            "DELEGATE: MarketAnalyst | What is the industry benchmark conversion rate?",
            "Final Synthesis: Projected revenue is $8,400 with a conversion rate benchmark of 3.5%.",
        ]
    )

    lead_supervisor = Agent(
        name="ProjectLead",
        role="Executive Coordinator",
        instructions="Coordinate workers to provide a comprehensive market analysis.",
        llm=supervisor_llm,
    )

    hierarchical = HierarchicalSupervisor(
        supervisor=lead_supervisor,
        workers=[math_worker, research_worker],
        max_delegations=4,
    )

    task = "Prepare financial forecast for Q3 campaign."
    print(f"Goal: {task}\n")

    result = await hierarchical.run(task)

    print("Workflow Timeline:")
    for msg in result.messages:
        print(f"[{msg.sender}] ({msg.role.value}): {msg.content}")

    print(f"\nFinal Executive Answer:\n{result.final_text}")


if __name__ == "__main__":
    asyncio.run(main())
