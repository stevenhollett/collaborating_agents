# collaborating_agents

[![Version](https://img.shields.io/badge/version-0.2.0-blue.svg)](#versioning)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10+-brightgreen.svg)](https://www.python.org/)

A flexible multi-topology Python framework for having multiple autonomous agents work together to solve complex problems.

---

## Key Features

- **Multi-Topology Collaboration**:
  - **Sequential Pipeline**: Ordered multi-stage workflows where each agent refines or builds upon the previous agent's output (e.g., Researcher &rarr; Analyst &rarr; Writer).
  - **Group Chat**: Shared discussion room with configurable turn-taking (Round-Robin, Moderator-driven, or Custom Selector) and termination conditions.
  - **Hierarchical Supervisor**: Central coordinator agent equipped with subtask delegation tools or directives to manage specialized worker agents and synthesize results.
- **Pluggable LLM Providers**:
  - `MockLLMClient`: Zero-dependency deterministic client for testing, CI/CD, and simulated scenarios.
  - `CallableLLMClient`: Custom Python callable / rule-based backend.
  - `GeminiLLMClient`: Native Google Gemini client integration via the `google-genai` SDK.
- **Tool Support**: Decorate any sync or async Python function with `@tool` to expose tools to agents.
- **Zero-Dependency Core**: The core framework runs entirely on Python 3 standard library (`asyncio`, `dataclasses`, `typing`, `json`, `unittest`).

---

## Installation

```bash
# Clone the repository
git clone git@github.com:stevenhollett/collaborating_agents.git
cd collaborating_agents

# Editable install with optional Gemini provider
pip install -e .
pip install -e ".[gemini]"
```

---

## Quickstart

### 1. Sequential Pipeline
```python
import asyncio
from collaborating_agents import Agent, SequentialPipeline
from collaborating_agents.llm import MockLLMClient

async def main():
    researcher = Agent(name="Researcher", llm=MockLLMClient(default_response="Key findings found."))
    writer = Agent(name="Writer", llm=MockLLMClient(default_response="Polished report drafted."))
    
    pipeline = SequentialPipeline([researcher, writer])
    result = await pipeline.run("Analyze market trends")
    print(result.final_text)

asyncio.run(main())
```

### 2. Group Chat
```python
import asyncio
from collaborating_agents import Agent, GroupChat
from collaborating_agents.llm import MockLLMClient

async def main():
    agent_a = Agent(name="Alice", llm=MockLLMClient(responses=["I suggest plan A."]))
    agent_b = Agent(name="Bob", llm=MockLLMClient(responses=["TERMINATE: Plan A is approved."]))

    chat = GroupChat(agents=[agent_a, agent_b], termination_keyword="TERMINATE")
    result = await chat.run("Select the deployment plan")
    print(result.final_text)

asyncio.run(main())
```

### 3. Hierarchical Supervisor
```python
import asyncio
from collaborating_agents import Agent, HierarchicalSupervisor
from collaborating_agents.llm import MockLLMClient

async def main():
    worker = Agent(name="Worker", llm=MockLLMClient(default_response="Task complete."))
    supervisor = Agent(
        name="Supervisor",
        llm=MockLLMClient(responses=[
            "DELEGATE: Worker | Execute task",
            "Synthesized solution."
        ])
    )

    orchestrator = HierarchicalSupervisor(supervisor=supervisor, workers=[worker])
    result = await orchestrator.run("Solve problem")
    print(result.final_text)

asyncio.run(main())
```

---

## Running Verification & Tests

```bash
# Run the complete test suite
PYTHONPATH=src python3 -m unittest discover -s tests -v

# Run the runnable demo examples
PYTHONPATH=src python3 examples/sequential_pipeline_demo.py
PYTHONPATH=src python3 examples/group_chat_debate_demo.py
PYTHONPATH=src python3 examples/supervisor_delegation_demo.py
```

---

## Agent Guidelines & Rules

This project follows the agent guidelines defined in [`AGENTS.md`](./AGENTS.md) and managed via the [`.agents-rules`](./.agents-rules) submodule.

## Versioning

Current project version: **v0.2.0**
