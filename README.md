# Project Jarvis X

Project Jarvis X is a modular, extensible, debuggable, offline-first personal AI operating system scaffold.

It is not a chatbot. The core is an event-driven multi-agent runtime where Alfred routes work, Hermes carries events, Edith represents the mobile execution layer, and specialist agents remain idle until a task requires them.

## What is included

- Alfred orchestrator with intent, agent, and model routing.
- Hermes in-process event bus with trace IDs and target-based delivery.
- Agent registry and sandbox-friendly base agent contracts.
- Specialist agent stubs for Memory, Device, Research, Planner, Editing, CAD, ShadowBroker, and Debug.
- Tool layer with Markdown-backed Obsidian memory, Android-device planning, notification, and research placeholders.
- Mission System v1 with quests, boss fights, XP, streaks, and recovery missions.
- Alfred local REST API and lightweight Edith HTTP client.
- Structured JSON logging, failure reports, and health checks.
- Unit tests for routing, event delivery, memory, health checks, and failure reporting.

## Quick start

```powershell
cd outputs/project-jarvis-x
python -m unittest discover -s tests
$env:PYTHONPATH = "src"
python -m jarvisx "Open YouTube"
python -m jarvisx "remember Jarvis X should stay modular"
python -m jarvisx --serve --host 127.0.0.1 --port 8765
```

## Memory v1

Memory v1 uses an Obsidian-compatible Markdown vault as the local-first backend. The vault path is configurable through `create_default_runtime(obsidian_vault=Path(...))`; if omitted, Jarvis X uses `var/obsidian-vault`.

The Memory Tool automatically creates and repairs these folders:

- `Daily/`
- `Projects/`
- `Preferences/`
- `Conversations/`
- `Architecture/`
- `Scratchpad/`

Supported categories route to folders as follows:

- `preference` -> `Preferences/`
- `project` -> `Projects/`
- `conversation` -> `Conversations/`
- `architecture` -> `Architecture/`
- `general` -> `Scratchpad/`

Memory operations are exposed only through `LocalMemoryTool`:

- `save_memory(text, category)`
- `search_memory(query)`
- `append_daily_note(text)`
- `get_daily_note()`
- `list_memories(category)`

Search is keyword-only. There are no embeddings, vector databases, or RAG components in Memory v1.

## Mission System v1

Mission System v1 is a momentum layer, not a traditional todo app. It tracks continuity through narrative mission types, XP, progress, streaks, and recovery missions after inactivity.

Mission types:

- `main_quest`
- `side_quest`
- `boss_fight`
- `daily_mission`
- `recovery_mission`

Mission operations are exposed through `MissionTool`:

- `create_mission()`
- `complete_mission()`
- `list_active_missions()`
- `get_next_mission()`
- `generate_recovery_mission()`

Mission data is persisted as append-only mission events through `LocalMemoryTool.save_memory(..., "project")`. The Mission Tool does not read or write vault files directly; it reconstructs state from project memory records.

## Edith Communication v1

Alfred exposes a local-first REST API for Edith. Edith is a lightweight HTTP client and talks only to Alfred; it never calls specialist agents directly. Alfred delegates through Hermes for internal routing.

Start the API:

```powershell
$env:PYTHONPATH = "src"
python -m jarvisx --serve --host 127.0.0.1 --port 8765
```

Endpoints:

- `POST /chat`
- `GET /status`
- `POST /status`
- `POST /notify`
- `POST /device_action`

Supported device actions:

- `open_app`
- `notification`
- `speak_text`

All request and response payloads include a trace ID. Clients can provide `trace_id` in the JSON body or `X-Trace-ID` in the header; Alfred generates one when omitted.

Example Edith client usage:

```python
from jarvisx.clients.edith import EdithClient

edith = EdithClient(base_url="http://127.0.0.1:8765")
response = edith.device_action(
    "open_app",
    {"app_name": "YouTube"},
    trace_id="edith-demo-1",
)
```

## Architecture principles

1. Alfred decides and delegates. Specialists do specialized work.
2. Hermes is the only communication path between agents.
3. Agents use tools; tools perform actions.
4. The core is standard-library only and offline-first.
5. Every event has a trace ID.
6. Every failure can produce a structured report.
7. New features are added by creating a new agent folder/class, registering it, and assigning tools.

See [docs/architecture.md](docs/architecture.md), [docs/extending-agents.md](docs/extending-agents.md), and [docs/debugging.md](docs/debugging.md).
