from __future__ import annotations

import inspect
import os
from typing import Any, Callable, Dict, List, Optional, Union

from collaborating_agents.llm.base import BaseLLMClient, LLMResponse
from collaborating_agents.message import Message
from collaborating_agents.tool import Tool


class MockLLMClient(BaseLLMClient):
    """Deterministic LLM client designed for testing, offline execution, and validation."""

    def __init__(
        self,
        default_response: str = "Acknowledge.",
        responses: Optional[List[str]] = None,
        tool_call_sequence: Optional[List[List[Dict[str, Any]]]] = None,
    ) -> None:
        self.default_response = default_response
        self._responses: List[str] = list(responses) if responses else []
        self._tool_call_sequence: List[List[Dict[str, Any]]] = (
            list(tool_call_sequence) if tool_call_sequence else []
        )
        self.call_history: List[List[Message]] = []

    async def generate(
        self,
        messages: List[Message],
        tools: Optional[List[Tool]] = None,
        **kwargs: Any,
    ) -> LLMResponse:
        self.call_history.append(messages)

        content = self._responses.pop(0) if self._responses else self.default_response
        tool_calls = (
            self._tool_call_sequence.pop(0) if self._tool_call_sequence else None
        )

        return LLMResponse(
            content=content,
            tool_calls=tool_calls,
            usage={"total_tokens": len(content.split())},
        )


class CallableLLMClient(BaseLLMClient):
    """LLM client powered by a custom synchronous or asynchronous callable."""

    def __init__(
        self,
        handler: Callable[[List[Message], Optional[List[Tool]]], Union[str, LLMResponse]],
    ) -> None:
        self.handler = handler

    async def generate(
        self,
        messages: List[Message],
        tools: Optional[List[Tool]] = None,
        **kwargs: Any,
    ) -> LLMResponse:
        if inspect.iscoroutinefunction(self.handler):
            res = await self.handler(messages, tools)
        else:
            res = self.handler(messages, tools)

        if isinstance(res, LLMResponse):
            return res
        return LLMResponse(content=str(res))


class GeminiLLMClient(BaseLLMClient):
    """Client for Google Gemini models via the google-genai SDK."""

    def __init__(
        self,
        model: str = "gemini-2.5-flash",
        api_key: Optional[str] = None,
    ) -> None:
        self.model = model
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")

    async def generate(
        self,
        messages: List[Message],
        tools: Optional[List[Tool]] = None,
        **kwargs: Any,
    ) -> LLMResponse:
        try:
            from google import genai
            from google.genai import types
        except ImportError:
            raise ImportError(
                "The 'google-genai' package is required for GeminiLLMClient. "
                "Install it with: pip install google-genai"
            )

        client = genai.Client(api_key=self.api_key)
        
        # Build contents from messages
        contents = []
        for msg in messages:
            contents.append(f"{msg.sender} ({msg.role.value}): {msg.content}")
        prompt_text = "\n\n".join(contents)

        # Call generate_content (blocking in thread if async wrapper needed)
        import asyncio
        response = await asyncio.to_thread(
            client.models.generate_content,
            model=self.model,
            contents=prompt_text,
        )

        return LLMResponse(
            content=response.text or "",
            raw_response=response,
        )
