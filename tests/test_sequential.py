import unittest
from collaborating_agents.agent import Agent
from collaborating_agents.llm.providers import MockLLMClient
from collaborating_agents.orchestrators.sequential import SequentialPipeline


class TestSequentialPipeline(unittest.IsolatedAsyncioTestCase):
    async def test_sequential_chain(self):
        agent1 = Agent(
            name="Researcher",
            llm=MockLLMClient(default_response="Key findings: agents collaborate."),
        )
        agent2 = Agent(
            name="Writer",
            llm=MockLLMClient(default_response="Draft article based on findings."),
        )
        agent3 = Agent(
            name="Editor",
            llm=MockLLMClient(default_response="Final polished publication."),
        )

        pipeline = SequentialPipeline(agents=[agent1, agent2, agent3])
        result = await pipeline.run("Analyze collaboration in AI agents")

        self.assertTrue(result.successful)
        self.assertEqual(result.final_text, "Final polished publication.")
        self.assertEqual(len(result.messages), 4)  # User prompt + 3 agent responses
        self.assertEqual(result.messages[1].sender, "Researcher")
        self.assertEqual(result.messages[2].sender, "Writer")
        self.assertEqual(result.messages[3].sender, "Editor")


if __name__ == "__main__":
    unittest.main()
