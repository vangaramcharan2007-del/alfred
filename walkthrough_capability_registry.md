# Capability Registry Walkthrough

This document summarizes the changes made during the Capability-Based Multi-Agent Intelligence upgrade.

## 1. Architecture Changes

- **Agent Manifest Protocol**: We introduced `AgentManifest` and standard JSON manifests in `src/jarvisx/agents/manifests/`. Agents like Friday, Edith, and Vision now declare their capabilities, tools, and resource requirements explicitly in JSON format.
- **Capability Registry**: Created `src/jarvisx/agents/capability_registry.py` with the `CapabilityRegistry` class. It sits above `AgentRegistry` and provides intelligence on *which* agent should handle a task by matching required capabilities against the manifests. It ranks agents by capability match and priority.
- **Upgraded OmniRouter**: Modified `src/jarvisx/core/llm_router.py` to add a `route_task` method. Instead of just picking an agent by name, the router asks the LLM to extract the user's `intent` and `required_capabilities`, and optionally use the `CapabilityRegistry` to select the agents based on those capabilities.
- **Memory-Aware Routing**: Updated `src/jarvisx/agents/alfred.py`. Before invoking the router, Alfred fetches `active_missions` from `MissionTool` and `recent_projects` from `LocalMemoryTool` and injects them into the context, allowing the router to make contextually-aware decisions.
- **Agent Monitoring**: Created `src/jarvisx/agents/agent_monitor.py` which tracks agent health, latency, success rates, and availability. It supports node tagging for future distributed deployment.

## 2. Execution Flow

When a user prompts Jarvis X (e.g. "Create a reminder on my phone"):

1. Alfred receives the message.
2. Alfred fetches context (missions, memories).
3. Alfred calls `OmniRouterClient.route_task()`.
4. The LLM extracts:
   - Intent: "reminder"
   - Required capabilities: ["mobile_control", "reminders"]
5. The `CapabilityRegistry` searches for agents with these capabilities.
6. `Edith` matches the required capabilities with a high confidence score.
7. The routing payload is returned to Alfred.
8. Alfred delegates the task to Edith via `HermesBus`.

## 3. Testing Results

All tests have successfully passed:
- `tests/test_capability_registry.py`: Validated manifest loading and capability discovery/ranking logic.
- `tests/test_dynamic_routing.py`: Validated the JSON schema parsing and fallback mechanisms in `OmniRouterClient`.
- `tests/test_agent_health.py`: Validated heartbeat and success rate tracking.
- `scripts/acceptance_test.py`: Passed all end-to-end routing sequences with the new dynamic capability router.
