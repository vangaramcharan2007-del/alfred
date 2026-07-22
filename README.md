# Project Jarvis X

Project Jarvis X: Intelligent Offline OS
An autonomous, offline-first operating system powered by embodied AI, featuring persistent memory, dynamic capability negotiation, and native Skill Intelligence.

## Native Jarvis X Skill Intelligence Layer

The Skill Intelligence Layer introduces Hermes-inspired concepts directly into Jarvis X:
- **Skill Architecture:** Encapsulates complex logic and tool selection (e.g. `ResearchSkill`).
- **Dynamic Discovery:** Agents can query the `SkillRegistry` for currently available capabilities.
- **Workflow Reuse:** The `WorkflowManager` extracts successful execution chains and stores them in the `workspace/workflows/` directory for later reuse.
- **Strict OmniRoute Coupling:** All skill logic interacts strictly with the OmniRoute Gateway via `OmniRouterClient`, ensuring offline-fallback resilience.

### Alfred Capability Intelligence Layer (Phase E.5)
Alfred features a hybrid capability decision layer, shifting from manual skill selection to an intelligent autonomous matching system:
- **Before:** `User → Manual Skill`
- **After:** `User → Alfred → Capability Matcher → Skill Ranker → Skill Executor → Workflow Update`
- **Capability Matcher:** Evaluates mission steps against available skills using a hybrid approach: Rules -> Tags -> Workflow History -> LLM Classification (OmniRoute fallback).
- **Skill Ranker:** Ranks candidates based on relevance (40%), historical success rate (30%), available permissions (20%), and execution cost (10%). Includes cooldown penalties to prevent infinite loops.
- **Persistence:** Skill execution results and duration are logged in the SQLite Database to dynamically adjust success rates over time.

*(Note: The Hermes Agent was evaluated as an architectural reference. Direct source integration pending successful repository inspection due to network constraints).* The core is an event-driven multi-agent runtime where Alfred routes work, Hermes carries events, Edith represents the mobile execution layer, and specialist agents remain idle until a task requires them.

## External Capability Integrations

### ShadowBroker OSINT Integration
Jarvis X integrates the ShadowBroker decentralized OSINT platform as a modular skill capability:
- **Adapter**: `ShadowBrokerAdapter` wraps the official client, standardizing HMAC signing and enforcing timeout/failure degradation.
- **Skill**: `ShadowBrokerOSINT` exposes fast-path capabilities (`ask`, `run_playbook`, `channel_status`) to the Agent Runtime.
- **Permissions**: Full boundary enforcement. The adapter requires `network_access` and uses the Jarvis X `PermissionManager` to block unapproved external calls.
- **Data Boundary**: ShadowBroker operates without access to Jarvis X memory or user profiles. All LLM reasoning remains internally gated through `OmniRoute`.

## Installation


### Option 1: Docker (Recommended)
The easiest way to run Jarvis X is via Docker Compose. This ensures all dependencies (like Tesseract OCR) are isolated and configured correctly.

```bash
git clone https://github.com/vangaramcharan2007-del/alfred.git
cd alfred
docker-compose up -d
```
This will start the Jarvis API and Dashboard on port `8765`.

### Option 2: Local Python Installation
Clone the repository and install the dependencies. You must have Python 3.11+ installed.

## What is included

- Alfred orchestrator with intent, agent, and model routing.
- Hermes in-process event bus with trace IDs and target-based delivery.
- Agent registry and sandbox-friendly base agent contracts.
- **Dynamic Plugin Ecosystem**: Auto-discovery and loading of agents via `src/jarvisx/plugins/`.
- Specialist agents: Memory, Device, Research, Planner, Editing, CAD, ShadowBroker, Debug, and XP.
- Tool layer: Obsidian memory, Android MacroDroid intents, Termux API, OpenSCAD CAD generator, notification, and research.
- **Mission & Gamification (XP) System v1**: Quests, boss fights, XP, streaks, and level tracking.
- **Voice Interaction**: Local fallback with ElevenLabs (TTS) and OpenAI Whisper (STT) integrations.
- **GUI Dashboard**: Lightweight local HTTP dashboard for system state monitoring, logs, and mode switching.
- **Operational Backend**: Local SQLite cache with robust background synchronization to Supabase.
- **Edith Mobile System**: Deep integration with Android via Termux (`termux-api`).
- Personality and Modes v1 for style-only communication adaptation.
- Alfred local REST API and lightweight Edith HTTP client.
- Structured JSON logging, failure reports, health checks, and in-memory ring buffers.
- Unit tests covering 95%+ of core routing, memory, tools, and sync logic.

## Quick start

```powershell
# Windows
.\bootstrap.ps1
```

```bash
# Unix/Linux/Termux
./bootstrap.sh
```

Alternatively, manual startup:
```powershell
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

## Personality and Modes v1

Personalities and modes adapt communication style without changing logic, routing, permissions, model selection, or execution.

Built-in personalities:

- Alfred
- Edith
- Hermes

Supported modes:

- `focus`
- `study`
- `builder`
- `research`
- `companion`
- `emergency`

Personalization operations are exposed through `PersonalizationTool`:

- `set_mode()`
- `get_mode()`
- `set_personality()`
- `get_personality()`
- `list_modes()`
- `list_personalities()`

State is stored through Memory Tool in `Preferences/`. Runtime startup restores the active mode and saved personalities by replaying preference events. Custom future-agent profiles can be saved with communication-style fields such as `tone`, `style`, `verbosity`, `warmth`, `examples`, `pacing`, and `notes`.

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

## Android Adapter v1

Device actions are converted by `DeviceTool` into MacroDroid-compatible Android broadcast intent payloads. The adapter prepares local intent data only; execution remains on Edith or the Android device.

MacroDroid trigger contract:

- Broadcast action: `com.projectjarvisx.MACRODROID_INTENT`
- Package hint: `com.arlosoft.macrodroid`
- Extras include `jarvis_action` and `trace_id`

Supported `jarvis_action` values:

- `open_app`
- `notification`
- `speak_text`

The route remains `Edith -> Alfred REST API -> Hermes -> Device Agent -> DeviceTool -> MacroDroid intent`.

## Architecture principles

1. Alfred decides and delegates. Specialists do specialized work.
2. Hermes is the only communication path between agents.
3. Agents use tools; tools perform actions.
4. The core is standard-library only and offline-first.
5. Every event has a trace ID.
6. Every failure can produce a structured report.
7. New features are added by creating a new agent folder/class, registering it, and assigning tools.

See [docs/architecture.md](docs/architecture.md), [docs/extending-agents.md](docs/extending-agents.md), and [docs/debugging.md](docs/debugging.md).
