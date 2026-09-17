import unittest
from collaborating_agents.agent import Agent
from collaborating_agents.llm.providers import MockLLMClient
from collaborating_agents.orchestrators.hierarchical import HierarchicalSupervisor


class TestHierarchicalSupervisor(unittest.IsolatedAsyncioTestCase):
    async def test_hierarchical_tool_delegation(self):
        coder = Agent(
            name="Coder",
            role="Software Engineer",
            llm=MockLLMClient(default_response="def solve(): return 42"),
        )
        tester = Agent(
            name="Tester",
            role="QA Engineer",
            llm=MockLLMClient(default_response="Tests passed successfully."),
        )

        supervisor_llm = MockLLMClient(
            responses=[
                "Delegating to coder.",
                "All tasks verified. The implementation is complete.",
            ],
            tool_call_sequence=[
                [
                    {
                        "id": "del_1",
                        "name": "delegate_to_worker",
                        "arguments": {
                            "worker_name": "Coder",
                            "subtask": "Write solve() function",
                        },
                    }
                ]
            ],
        )

        supervisor = Agent(
            name="Supervisor",
            role="Technical Lead",
            llm=supervisor_llm,
        )

        orchestrator = HierarchicalSupervisor(
            supervisor=supervisor,
            workers=[coder, tester],
            max_delegations=3,
        )

        result = await orchestrator.run("Implement and verify solve function")

        self.assertTrue(result.successful)
        self.assertIn("All tasks verified", result.final_text)

    async def test_hierarchical_text_directive_delegation(self):
        worker = Agent(
            name="Analyst",
            role="Financial Analyst",
            llm=MockLLMClient(default_response="Revenue increased by 15%."),
        )
        supervisor_llm = MockLLMClient(
            responses=[
                "DELEGATE: Analyst | Compute revenue delta",
                "Summary: The fiscal health is positive based on analyst findings.",
            ]
        )
        supervisor = Agent(name="Lead", role="Manager", llm=supervisor_llm)

        orchestrator = HierarchicalSupervisor(
            supervisor=supervisor,
            workers=[worker],
            max_delegations=3,
        )

        result = await orchestrator.run("Prepare financial update")
        self.assertTrue(result.successful)
        self.assertIn("Summary: The fiscal health is positive", result.final_text)


if __name__ == "__main__":
    unittest.main()
