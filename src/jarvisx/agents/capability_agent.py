from __future__ import annotations

import dataclasses
from typing import Any, Optional

from jarvisx.agents.base import BaseAgent, AgentResponse
from jarvisx.core.events import Event
from jarvisx.core.failures import FailureReport
from jarvisx.core.logging import StructuredLogger
from jarvisx.core.capabilities.base import Capability, ProviderError
from jarvisx.core.capabilities.runtime import CapabilityRuntime


class CapabilityAgent(BaseAgent):
    """
    Internal infrastructure agent that bridges Hermes tasks to the CapabilityRuntime.
    Alfred/Planner delegates to this agent to execute concrete capabilities.
    """
    agent_id = "capability_engine"
    role = "Capability Executor"
    capabilities = ("BROWSER", "COMMUNICATION", "DESKTOP", "FILE_SYSTEM")

    def __init__(self, runtime: CapabilityRuntime, logger: Optional[StructuredLogger] = None):
        super().__init__(logger=logger)
        self.capability_runtime = runtime

    async def handle(self, event: Event) -> AgentResponse:
        """
        Handles execution of a specific capability.
        Expected payload:
        {
            "capability_name": "BROWSER" | "COMMUNICATION" | "DESKTOP" | ...,
            "task": {"action": "...", ...}
        }
        """
        payload = event.payload
        cap_name = payload.get("capability_name")
        task_data = payload.get("task")
        
        if not cap_name or not task_data:
            return self._error_response(
                event, "capability_missing_args", "Task payload must include capability_name and task dict."
            )

        try:
            # Map string to enum safely
            capability = Capability[cap_name.upper()]
        except KeyError:
            return self._error_response(
                event, "capability_invalid", f"Capability '{cap_name}' is not recognized."
            )

        try:
            result = self.capability_runtime.execute(capability, task_data)
            return self._response(
                event,
                handled=True,
                message=result.get("message", "Task completed successfully."),
                data={"result": result},
            )
        except ProviderError as e:
            return self._error_response(event, "provider_error", str(e))
        except Exception as e:
            return self._error_response(event, "execution_error", f"An unexpected error occurred: {str(e)}")

    def _error_response(self, event: Event, fail_type: str, why: str) -> AgentResponse:
        failure = FailureReport(
            what_failed=fail_type,
            why=why,
            agent_id=self.agent_id,
            tool_name=None,
            proposed_fix="Check capability payload format and provider availability.",
            trace_id=event.trace_id,
        )
        return self._response(
            event,
            handled=False,
            message=f"Capability execution failed: {why}",
            data={"failure": failure.to_dict()},
        )
