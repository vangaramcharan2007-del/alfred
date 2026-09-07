from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional


@dataclass(slots=True)
class AgentResponse:
    success: bool
    message: str
    data: Optional[Any] = None


class EV:
    __slots__ = ("name", "alias", "_commands")

    def __init__(self, name: str = "E.V.", alias: str = "Friday") -> None:
        self.name: str = name
        self.alias: str = alias
        self._commands: Dict[str, Callable[..., Any]] = {}

    def register_command(self, name: str, func: Callable[..., Any]) -> None:
        self._commands[name.lower().strip()] = func

    def greet(self, user_name: Optional[str] = None) -> str:
        target = f", {user_name}" if user_name else ""
        return f"Hello{target}. I am {self.name}, also known as {self.alias}. Online and ready."

    def answer_query(self, query: str) -> AgentResponse:
        cleaned_query = query.strip()
        if not cleaned_query:
            return AgentResponse(success=False, message="Query cannot be empty.")
        
        return AgentResponse(
            success=True,
            message=f"Query processed: '{cleaned_query}'",
            data={"query": cleaned_query, "status": "resolved"}
        )

    def execute_command(self, command_name: str, *args: Any, **kwargs: Any) -> AgentResponse:
        key = command_name.lower().strip()
        handler = self._commands.get(key)
        
        if not handler:
            return AgentResponse(
                success=False,
                message=f"Unknown command: '{command_name}'"
            )

        try:
            result = handler(*args, **kwargs)
            return AgentResponse(
                success=True,
                message=f"Command '{key}' executed successfully.",
                data=result
            )
        except Exception as exc:
            return AgentResponse(
                success=False,
                message=f"Execution error in '{key}': {exc}"
            )


Friday = EV
