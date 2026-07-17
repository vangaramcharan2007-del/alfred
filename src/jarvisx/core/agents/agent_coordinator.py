"""Agent Coordinator — orchestrates delegation, parallel execution, and failure recovery."""
import asyncio
import logging
import time
import uuid
from typing import Dict, Any, List, Optional

from .agent_identity import AgentIdentity, AgentState
from .agent_registry import AgentRegistry
from .message_bus import MessageBus, Message, MessageType
from .shared_context import SharedContext
from .resource_manager import ResourceManager
from .agent_metrics import AgentMetrics
from jarvisx.core.tools.tool_registry import ToolRegistry

logger = logging.getLogger(__name__)


class SubObjective:
    """A delegated piece of work assigned to a specialist agent."""

    def __init__(
        self,
        objective_id: str,
        description: str,
        parent_objective_id: str,
        required_capability: str,
        tool_name: str,
        method_name: str,
        args: Dict[str, Any],
    ):
        self.objective_id = objective_id
        self.description = description
        self.parent_objective_id = parent_objective_id
        self.required_capability = required_capability
        self.tool_name = tool_name
        self.method_name = method_name
        self.args = args
        self.owner_agent_id: Optional[str] = None
        self.state = "PENDING"
        self.evidence: Dict[str, Any] = {}
        self.error: Optional[str] = None


class AgentCoordinator:
    """Orchestrates multi-agent execution: delegation, parallel dispatch, failure recovery."""

    def __init__(
        self,
        agent_registry: AgentRegistry,
        tool_registry: ToolRegistry,
        message_bus: Optional[MessageBus] = None,
        shared_context: Optional[SharedContext] = None,
        resource_manager: Optional[ResourceManager] = None,
    ):
        self.agent_registry = agent_registry
        self.tool_registry = tool_registry
        self.message_bus = message_bus or MessageBus.get_instance()
        self.shared_context = shared_context or SharedContext.get_instance()
        self.resource_manager = resource_manager or ResourceManager.get_instance()
        self._agent_metrics: Dict[str, AgentMetrics] = {}

    def get_agent_metrics(self, agent_id: str) -> AgentMetrics:
        if agent_id not in self._agent_metrics:
            self._agent_metrics[agent_id] = AgentMetrics(agent_id)
        return self._agent_metrics[agent_id]

    async def execute_multi_agent_objective(
        self,
        objective: str,
        sub_tasks: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Execute an objective by delegating sub-tasks to specialist agents."""

        parent_id = f"obj_{uuid.uuid4().hex[:8]}"
        logger.info(f"Multi-agent objective [{parent_id}]: {objective}")

        # Build SubObjective list
        sub_objectives: List[SubObjective] = []
        for task in sub_tasks:
            sub_obj = SubObjective(
                objective_id=task.get("id", f"sub_{uuid.uuid4().hex[:6]}"),
                description=task.get("description", ""),
                parent_objective_id=parent_id,
                required_capability=task.get("required_capability", task.get("tool", "")),
                tool_name=task.get("tool", ""),
                method_name=task.get("method", ""),
                args=task.get("args", {}),
            )
            sub_objectives.append(sub_obj)

        # Delegate and execute
        results = await self._delegate_and_execute(sub_objectives)

        # Record to shared context
        all_success = all(r["success"] for r in results)
        self.shared_context.record_completed_objective({
            "objective_id": parent_id,
            "objective": objective,
            "success": all_success,
            "sub_results": results,
            "timestamp": time.time(),
        })

        # Persist metrics
        for metrics in self._agent_metrics.values():
            metrics.persist()
        self.shared_context.persist()

        return {
            "objective_id": parent_id,
            "success": all_success,
            "results": results,
        }

    async def _delegate_and_execute(
        self, sub_objectives: List[SubObjective]
    ) -> List[Dict[str, Any]]:
        """Assign sub-objectives to agents and execute in parallel."""

        # Phase 1: Assignment
        for sub in sub_objectives:
            agent = self._find_agent(sub.required_capability)
            if agent:
                sub.owner_agent_id = agent.agent_id
                agent.assign_objective(sub.objective_id)
                metrics = self.get_agent_metrics(agent.agent_id)
                metrics.record_delegation()

                # Send task request via message bus
                await self.message_bus.send(Message(
                    sender_id="coordinator",
                    recipient_id=agent.agent_id,
                    msg_type=MessageType.TASK_REQUEST,
                    payload={
                        "objective_id": sub.objective_id,
                        "tool": sub.tool_name,
                        "method": sub.method_name,
                        "args": sub.args,
                    },
                ))
            else:
                sub.state = "UNASSIGNED"
                sub.error = f"No available agent for capability '{sub.required_capability}'"

        # Phase 2: Parallel execution
        tasks = [self._execute_sub_objective(sub) for sub in sub_objectives]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Phase 3: Collect results
        final_results = []
        for sub, result in zip(sub_objectives, results):
            if isinstance(result, Exception):
                final_results.append({
                    "objective_id": sub.objective_id,
                    "success": False,
                    "error": str(result),
                    "agent_id": sub.owner_agent_id,
                    "evidence": {},
                })
            else:
                final_results.append(result)

        return final_results

    async def _execute_sub_objective(self, sub: SubObjective) -> Dict[str, Any]:
        """Execute a single sub-objective, with failure recovery."""

        if sub.state == "UNASSIGNED":
            return {
                "objective_id": sub.objective_id,
                "success": False,
                "error": sub.error,
                "agent_id": None,
                "evidence": {},
            }

        agent_id = sub.owner_agent_id
        metrics = self.get_agent_metrics(agent_id)
        metrics.start_task(sub.objective_id)

        # Acquire resource lock
        resource_key = sub.tool_name
        lock_acquired = await self.resource_manager.acquire(resource_key, agent_id, timeout=15.0)

        try:
            if not lock_acquired:
                # Cannot proceed — resource contention
                metrics.fail_task(sub.objective_id)
                return {
                    "objective_id": sub.objective_id,
                    "success": False,
                    "error": f"Resource '{resource_key}' contention timeout",
                    "agent_id": agent_id,
                    "evidence": {},
                }

            # Execute via ToolRegistry
            result = await self.tool_registry.execute(sub.tool_name, sub.method_name, sub.args)

            if result.get("success"):
                sub.state = "COMPLETED"
                sub.evidence = result.get("evidence", {})
                metrics.complete_task(sub.objective_id)

                # Store evidence in shared context
                self.shared_context.store_evidence(sub.objective_id, sub.evidence)

                # Send result via bus
                await self.message_bus.send(Message(
                    sender_id=agent_id,
                    recipient_id="coordinator",
                    msg_type=MessageType.TASK_RESULT,
                    payload={"objective_id": sub.objective_id, "success": True, "evidence": sub.evidence},
                ))
            else:
                sub.state = "FAILED"
                sub.error = result.get("error", "Unknown")
                metrics.fail_task(sub.objective_id)

                # Attempt failure recovery: find replacement agent
                recovered = await self._attempt_recovery(sub, result)
                if recovered:
                    return recovered

                # Send error report
                await self.message_bus.send(Message(
                    sender_id=agent_id,
                    recipient_id="coordinator",
                    msg_type=MessageType.ERROR_REPORT,
                    payload={"objective_id": sub.objective_id, "error": sub.error},
                ))

            # Release agent's objective
            agent = self.agent_registry.get_agent(agent_id)
            if agent:
                agent.release_objective(sub.objective_id)

            return {
                "objective_id": sub.objective_id,
                "success": result.get("success", False),
                "error": result.get("error"),
                "agent_id": agent_id,
                "evidence": sub.evidence,
            }

        finally:
            if lock_acquired:
                self.resource_manager.release(resource_key, agent_id)

    async def _attempt_recovery(self, sub: SubObjective, original_result: Dict) -> Optional[Dict[str, Any]]:
        """Try to re-assign a failed task to an alternative agent."""
        if not sub.owner_agent_id:
            return None

        # Mark original agent failed for this task
        original_agent = self.agent_registry.get_agent(sub.owner_agent_id)
        if original_agent:
            original_agent.release_objective(sub.objective_id)

        # Find a replacement
        replacement = self.agent_registry.find_replacement(sub.owner_agent_id)
        if not replacement:
            self.shared_context.record_failure({
                "objective_id": sub.objective_id,
                "original_agent": sub.owner_agent_id,
                "error": sub.error,
                "recovery": "no_replacement_found",
            })
            return None

        logger.info(f"Recovery: reassigning {sub.objective_id} from {sub.owner_agent_id} to {replacement.agent_id}")
        sub.owner_agent_id = replacement.agent_id
        replacement.assign_objective(sub.objective_id)

        metrics = self.get_agent_metrics(replacement.agent_id)
        metrics.start_task(sub.objective_id)

        result = await self.tool_registry.execute(sub.tool_name, sub.method_name, sub.args)

        if result.get("success"):
            sub.state = "COMPLETED"
            sub.evidence = result.get("evidence", {})
            metrics.complete_task(sub.objective_id)
            self.shared_context.store_evidence(sub.objective_id, sub.evidence)
        else:
            sub.state = "FAILED"
            metrics.fail_task(sub.objective_id)

        replacement.release_objective(sub.objective_id)

        return {
            "objective_id": sub.objective_id,
            "success": result.get("success", False),
            "error": result.get("error"),
            "agent_id": replacement.agent_id,
            "evidence": sub.evidence,
            "recovered": True,
        }

    def _find_agent(self, capability: str) -> Optional[AgentIdentity]:
        """Find the best available agent for a capability."""
        capable = self.agent_registry.discover_capable(capability)
        if capable:
            # Prefer the agent with the fewest active objectives
            return min(capable, key=lambda a: len(a.active_objectives))
        return None
