# Architecture

## Core roles

### Alfred

Alfred is the executive orchestrator. It classifies intent, selects a specialist agent, selects a model profile, emits a task event through Hermes, and aggregates the response.

Alfred should not perform specialized work directly when a specialist exists.

### Edith

Edith is the mobile companion and Android execution layer. In this scaffold, Edith is represented as a lightweight agent that can route device-adjacent requests to the Device Agent. Real Android execution should be added through tools such as MacroDroid, ADB, or a local Android bridge.

### Hermes

Hermes is the communication bus. Agents do not call each other directly. They subscribe to event types, and Hermes delivers targeted events by agent ID.

## Event flow

```text
User message
  -> Alfred classifies intent
  -> Alfred selects agent and model profile
  -> Alfred publishes agent.task.requested to Hermes
  -> Hermes delivers the event to the targeted specialist
  -> Specialist uses tools and returns an AgentResponse
  -> Alfred aggregates the response
```

## Edith communication

Edith Communication v1 adds a local REST boundary owned by Alfred. Edith acts as a lightweight HTTP client and talks only to Alfred.

```text
Edith client
  -> Alfred REST API
  -> Alfred orchestration method
  -> Hermes agent.task.requested event
  -> Device Agent or selected specialist
  -> Tool result
  -> Alfred API response
```

Supported endpoints:

- `/chat`: routes free-form user text through Alfred intent classification.
- `/status`: returns runtime health checks.
- `/notify`: converts a notification request into a device action and routes it through Hermes.
- `/device_action`: routes supported device actions through the Device Agent.

Supported device actions:

- `open_app`
- `notification`
- `speak_text`

Each request either supplies a trace ID through `trace_id` or `X-Trace-ID`, or Alfred generates one. The same trace ID is carried through Hermes events and returned in the HTTP response.

Edith must not communicate directly with agents. Any future mobile transport, voice adapter, or MacroDroid bridge should remain behind the Edith client or device tools while keeping Alfred as the API gateway.

## Android adapter

Android Adapter v1 lives behind `DeviceTool`. It converts supported device actions into MacroDroid-compatible broadcast intent payloads without executing them directly.

The internal route is preserved:

```text
Alfred
  -> Hermes
  -> Device Agent
  -> DeviceTool
  -> MacroDroid intent payload
```

MacroDroid should listen for broadcast action `com.projectjarvisx.MACRODROID_INTENT`. The payload extras include:

- `jarvis_action`: one of `open_app`, `notification`, or `speak_text`
- `trace_id`: the Hermes/API trace ID
- action-specific values such as `app_name`, `package_hint`, `title`, `body`, or `text`

This adapter is local-first. It prepares the Android intent contract and leaves actual execution to Edith, MacroDroid, or a future Android bridge.

## Offline-first design

The base runtime uses only the Python standard library. Networked integrations such as Supabase, remote search, and hosted LLMs should be adapters behind tools or model providers. The system should continue to boot and route tasks even when those adapters are unavailable.

## Mission system

Mission System v1 is owned by the Planner Agent through `MissionTool`. It is designed for momentum and continuity rather than checklist management.

Supported mission types:

- `main_quest`
- `side_quest`
- `boss_fight`
- `daily_mission`
- `recovery_mission`

Supported operations:

- `create_mission()`
- `complete_mission()`
- `list_active_missions()`
- `get_next_mission()`
- `generate_recovery_mission()`

Mission persistence is append-only. The Mission Tool writes mission events through `LocalMemoryTool.save_memory(..., "project")` and reconstructs current state from project memory records. This keeps the vault boundary inside the Memory Tool while still allowing XP totals, progress, streaks, and inactivity recovery to be rebuilt offline.

Recovery missions are generated when continuity has been interrupted. They are intentionally small and high priority so the next suggested mission favors restart momentum.

## Memory layers

- Human-readable memory: Obsidian-compatible Markdown files in the configured vault.
- Structured memory: future Supabase adapter.
- Semantic memory: future embedding provider and vector index.

Memory v1 implements only the human-readable layer. The `LocalMemoryTool` is the sole vault boundary, and agents must never read or write vault files directly. Alfred reaches memory by routing work to the Memory Agent, and the Memory Agent calls tool methods.

The vault path is configurable. On startup or first use, the Memory Tool creates or repairs:

- `Daily/`
- `Projects/`
- `Preferences/`
- `Conversations/`
- `Architecture/`
- `Scratchpad/`

Category routing:

- `preference` -> `Preferences/`
- `project` -> `Projects/`
- `conversation` -> `Conversations/`
- `architecture` -> `Architecture/`
- `general` -> `Scratchpad/`

Supported Memory v1 operations:

- `save_memory(text, category)`
- `search_memory(query)`
- `append_daily_note(text)`
- `get_daily_note()`
- `list_memories(category)`

Search is simple keyword matching across Markdown files. Embeddings, vector databases, and RAG are intentionally excluded from this version.

## Debuggability

Each event carries:

- `id`
- `trace_id`
- `source`
- `target`
- `type`
- `timestamp`

Failures are normalized into `FailureReport` so operators can answer:

- What failed?
- Why did it fail?
- Which agent failed?
- Which tool failed?
- What is the proposed fix?
