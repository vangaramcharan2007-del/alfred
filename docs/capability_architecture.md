# Capability-Based Multi-Agent Intelligence

## Overview

Jarvis X has evolved its agent routing architecture from a static, rule-based matching system to a dynamic, capability-based intelligence system.

### Old: Rule-Based Routing
Previously, the `OmniRouterClient` and `AlfredOrchestrator` relied on static prompts that forced the LLM to pick an agent by name (e.g. `["friday", "edith"]`). This tight coupling meant that as new agents were added, the prompt grew unwieldy, and routing logic could not easily fallback or adapt to changing agent availability.

### New: Capability-Based Multi-Agent Intelligence
The new architecture introduces three core layers:

1. **Agent Manifests (`src/jarvisx/agents/manifests/*.json`)**
   Every agent now registers a standard manifest declaring its capabilities, input/output types, and resource requirements (e.g., GPU, internet).
   
2. **Capability Registry (`src/jarvisx/agents/capability_registry.py`)**
   The registry parses the manifests and acts as the intelligence layer to answer: *"Which agent can solve this problem?"*. It calculates a confidence score based on matched capabilities and agent priority.
   
3. **Memory-Aware Dynamic Routing (`src/jarvisx/core/llm_router.py`)**
   The user's prompt is routed through the LLM to extract the *intent* and *required_capabilities*.
   Before this extraction, Alfred queries the `MissionTool` and `LocalMemoryTool` to inject the user's active missions and recent projects into the prompt context.
   The extracted capabilities are then matched against the `CapabilityRegistry` to dynamically select the best agent for the task.

## Future: Distributed Nodes
The new `AgentMonitor` (`src/jarvisx/agents/agent_monitor.py`) tracks the health, latency, and success rates of agents. Its architecture includes `node` tagging, laying the groundwork for distributed setups (e.g., executing the Vision agent on a remote GPU node while the Editing agent runs locally).
