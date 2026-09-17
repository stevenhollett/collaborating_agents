import unittest
from collaborating_agents.agent import Agent
from collaborating_agents.llm.providers import MockLLMClient
from collaborating_agents.orchestrators.group_chat import GroupChat


class TestGroupChat(unittest.IsolatedAsyncioTestCase):
    async def test_group_chat_round_robin_and_termination(self):
        debater_a = Agent(
            name="Alice",
            llm=MockLLMClient(
                responses=[
                    "I suggest approach A.",
                    "I agree with the compromise.",
                ]
            ),
        )
        debater_b = Agent(
            name="Bob",
            llm=MockLLMClient(
                responses=[
                    "I propose approach B.",
                    "TERMINATE: We have reached consensus.",
                ]
            ),
        )

        chat = GroupChat(
            agents=[debater_a, debater_b],
            max_rounds=6,
            speaker_selection="round_robin",
            termination_keyword="TERMINATE",
        )

        result = await chat.run("Discuss architecture options")

        self.assertTrue(result.successful)
        self.assertIn("TERMINATE", result.final_text)
        # Sequence: task -> Alice (round 0) -> Bob (round 1) -> Alice (round 2) -> Bob (round 3 - terminates)
        self.assertEqual(len(result.messages), 5)
        self.assertEqual(result.messages[1].sender, "Alice")
        self.assertEqual(result.messages[2].sender, "Bob")
        self.assertEqual(result.messages[3].sender, "Alice")
        self.assertEqual(result.messages[4].sender, "Bob")


if __name__ == "__main__":
    unittest.main()
