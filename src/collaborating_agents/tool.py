from __future__ import annotations

import inspect
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional


@dataclass
class Tool:
    """Encapsulates a capability that an agent can invoke."""

    name: str
    description: str
    func: Callable[..., Any]
    parameters_schema: Dict[str, Any] = field(default_factory=dict)

    async def execute_async(self, **kwargs: Any) -> Any:
        """Executes the tool asynchronously, handling both sync and async underlying functions."""
        if inspect.iscoroutinefunction(self.func):
            return await self.func(**kwargs)
        return self.func(**kwargs)

    def execute(self, **kwargs: Any) -> Any:
        """Executes synchronous underlying function directly."""
        if inspect.iscoroutinefunction(self.func):
            import asyncio
            return asyncio.run(self.func(**kwargs))
        return self.func(**kwargs)

    def to_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters_schema,
        }


def tool(name: Optional[str] = None, description: Optional[str] = None) -> Callable[[Callable[..., Any]], Tool]:
    """Decorator to convert a Python function into an agent-executable Tool."""

    def decorator(fn: Callable[..., Any]) -> Tool:
        tool_name = name or fn.__name__
        tool_doc = description or (inspect.getdoc(fn) or "No description provided.")

        sig = inspect.signature(fn)
        properties: Dict[str, Any] = {}
        required: list[str] = []

        for param_name, param in sig.parameters.items():
            param_type = "string"
            if param.annotation is int:
                param_type = "integer"
            elif param.annotation is float:
                param_type = "number"
            elif param.annotation is bool:
                param_type = "boolean"
            elif param.annotation is list:
                param_type = "array"
            elif param.annotation is dict:
                param_type = "object"

            properties[param_name] = {"type": param_type}
            if param.default is inspect.Parameter.empty:
                required.append(param_name)

        schema = {
            "type": "object",
            "properties": properties,
            "required": required,
        }

        return Tool(
            name=tool_name,
            description=tool_doc,
            func=fn,
            parameters_schema=schema,
        )

    return decorator
