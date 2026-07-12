# Extending Agents

Add features by adding isolated agents and tools rather than modifying existing specialists.

## Add a new agent

1. Create an agent class that inherits from `BaseAgent`.
2. Give it a stable `agent_id`, role, expertise, tone, personality, and capabilities.
3. Assign only the tools it needs.
4. Register it in `jarvisx/runtime.py`.
5. Add intent keywords in `IntentClassifier` only if Alfred needs to route user tasks to it.
6. Add tests for routing and expected behavior.

## Agent rules

- Agents remain idle until Hermes delivers a targeted event.
- Agents communicate through Hermes rather than direct calls.
- Agents use tools for actions.
- Personality can shape response text, but it must never override logic.
- Debug Agent may suggest patches but must not deploy changes automatically.

## Tool rules

Tools perform actions. They should be small, replaceable, and independently testable.

Examples:

- `DeviceTool`: prepares or executes Android actions.
- `LocalMemoryTool`: stores and retrieves Markdown memory in the configured Obsidian vault.
- `MissionTool`: stores append-only mission events through `LocalMemoryTool`.
- `PersonalizationTool`: stores style-only mode and personality preferences through `LocalMemoryTool`.
- `NotificationTool`: sends or schedules notifications.
- `ResearchTool`: reads local docs now, web adapters later.

## Memory extension rules

- Preserve `LocalMemoryTool` as the only vault filesystem boundary.
- Add memory behavior through tool methods before changing agents.
- Keep Memory v1 keyword-only until a later architecture decision introduces semantic search.
- New memory categories must be added to the category map and covered by tests.

## Mission extension rules

- Mission data must persist through the Memory Tool.
- Do not make missions a conventional todo list; preserve XP, momentum, streak, and recovery semantics.
- New mission types must define XP and priority defaults.
- Mission state should remain reconstructable from append-only events.

## Android adapter rules

- Device actions must continue to flow through Alfred, Hermes, Device Agent, and Device Tool.
- Edith must not call agents or tools directly.
- MacroDroid payloads must include the current trace ID.
- New Android actions should be added to `SUPPORTED_DEVICE_ACTIONS`, implemented in `DeviceTool`, and covered by adapter tests.

## Personality and mode extension rules

- Add built-in modes in `src/jarvisx/config/personalization.py`.
- Add built-in personalities in `src/jarvisx/config/personalization.py`.
- Custom future-agent profiles should be stored with `PersonalizationTool.set_personality()`.
- Personality fields must remain communication-style fields only.
- Never allow mode or personality data to alter routing, permissions, execution, or model selection.
- Add tests for any new mode influence on response configuration or mission priority.
