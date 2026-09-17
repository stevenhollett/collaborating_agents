import unittest
from collaborating_agents.agent import Agent
from collaborating_agents.llm.providers import MockLLMClient
from collaborating_agents.message import Message, MessageRole
from collaborating_agents.tool import tool


class TestAgent(unittest.IsolatedAsyncioTestCase):
    async def test_agent_basic_step(self):
        client = MockLLMClient(default_response="Hello, world!")
        agent = Agent(name="TestAgent", instructions="Be helpful.", llm=client)

        input_msg = Message(role=MessageRole.USER, sender="user", content="Hi")
        response = await agent.step(input_message=input_msg)

        self.assertEqual(response.sender, "TestAgent")
        self.assertEqual(response.content, "Hello, world!")
        self.assertEqual(len(agent.memory), 2)  # input + output

    async def test_agent_tool_execution(self):
        @tool(name="add_numbers", description="Adds two numbers")
        def add_numbers(a: int, b: int) -> int:
            return a + b

        # 1st LLM call returns a tool call, 2nd LLM call returns final answer
        client = MockLLMClient(
            responses=["The sum is computed.", "The total is 42."],
            tool_call_sequence=[
                [{"id": "call_1", "name": "add_numbers", "arguments": {"a": 20, "b": 22}}]
            ],
        )

        agent = Agent(name="MathAgent", llm=client)
        agent.add_tool(add_numbers)

        res = await agent.step(Message(content="What is 20 + 22?"))
        self.assertEqual(res.content, "The total is 42.")
        self.assertEqual(res.sender, "MathAgent")


if __name__ == "__main__":
    unittest.main()
