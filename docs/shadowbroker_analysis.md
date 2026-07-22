# ShadowBroker Capability Analysis

## Overview
ShadowBroker is a decentralized intelligence platform that aggregates real-time OSINT telemetry. It is integrated into Jarvis X not as an agent or orchestrator, but purely as a **capability provider (skill)**.

## Architectural Boundaries

1. **Orchestration**: Jarvis X (Alfred) remains the master orchestrator. ShadowBroker does not make decisions.
2. **LLM Gateway**: ShadowBroker relies entirely on Jarvis X's `OmniRoute` gateway for any LLM inference it might require. ShadowBroker's native LLM configuration is ignored.
3. **Memory Isolation**: ShadowBroker has no access to Jarvis X's memory database, user profile, or mission history. It receives only isolated query context.
4. **Permissions**: ShadowBroker accesses the network via the Jarvis X Tool Registry and Permission Manager (`network_access`).

## Capability Mapping

| ShadowBroker Feature | Jarvis X Equivalent | Integration Decision |
|---------------------|--------------------|----------------------|
| `sb.ask()` | Skill Execution | Wrapped as the primary query tool within the `ShadowBrokerOSINT` skill. Provides route + execute logic. |
| `sb.run_playbook()` | Workflow Manager | Wrapped as a tool for executing predefined snapshot queries (e.g., `hot_snapshot`). |
| `sb.channel_status()` | Provider Health Check| Mapped to the `ShadowBrokerAdapter` health check method. |
| Full Telemetry (40+ layers)| Direct Access | Excluded from initial integration to preserve latency and context limits. Can be added as granular skills later. |

## Implementation Path
- **Adapter**: `src/jarvisx/integrations/shadowbroker/shadowbroker_adapter.py` will wrap the HTTP client, handling HMAC signing and timeouts.
- **Skill**: `src/jarvisx/core/skills/installed/shadowbroker_skill.py` will expose the fast-path capabilities to the Jarvis X agent runtime.
