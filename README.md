# 🎩 Alfred — Sovereign Desktop Butler & Autonomous Engineering OS

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Tests-51%20Passed-brightgreen?style=for-the-badge" alt="Tests" />
  <img src="https://img.shields.io/badge/Architecture-Sovereign%20Agentic-blue?style=for-the-badge" alt="Architecture" />
  <img src="https://img.shields.io/badge/Tools-FastMCP%20Kernel-orange?style=for-the-badge" alt="FastMCP" />
  <img src="https://img.shields.io/badge/Offline--First-Ollama%20Local-red?style=for-the-badge" alt="Offline First" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License" />
</p>

Alfred (Jarvis X) is a **sovereign, offline-first autonomous AI operating assistant and engineering system**. It unifies intent parsing, multi-step mission execution, local model routing (Ollama with OpenRouter fallbacks), desktop tool actuation, cognitive memory synthesis, and self-healing into an executive control plane.

---

## 🏗️ Architecture

```
                      ┌────────────────────────────────────────┐
                      │        Alfred Executive Core           │
                      │    (CLI, Web HUD, Voice Pipeline)      │
                      └───────────────────┬────────────────────┘
                                          │
                      ┌───────────────────▼────────────────────┐
                      │       Personal OS Runtime Kernel       │
                      └───────┬──────────────────────┬─────────┘
                              │                      │
            ┌─────────────────▼────────┐   ┌─────────▼────────────────┐
            │  Dynamic Orchestrator    │   │  Unified Mission Planner │
            │  - Sovereign Agent Loop  │   │  - Step Decomposition    │
            │  - Multi-Turn Reasoning  │   │  - Checkpoint Save/Load  │
            │  - Self-Refinement Gate  │   │  - Failure Classifier    │
            └─────────────────┬────────┘   └─────────┬────────────────┘
                              │                      │
            ┌─────────────────▼──────────────────────▼────────┐
            │               Tool Execution Kernel             │
            │  - FastMCP Schema Engine   - Permission Gateway │
            │  - Path Traversal Guard    - Circuit Breaker    │
            └─────────────────┬───────────────────────────────┘
                              │
            ┌─────────────────▼───────────────────────────────┐
            │            Sovereign Agent Workforce            │
            │  [Coding] [DevOps] [Research] [Governance]      │
            └─────────────────────────────────────────────────┘
```

---

## ✨ Key Subsystems

- **Agentic Harness Orchestration** (`src/jarvisx/agentic/`): the unified agentic stack — provider-agnostic model backends, schema-validated permission-gated tools, a real jailed sandbox (rlimits, timeouts, secret scrubbing), a budgeted think/act/observe loop, executable verification, DAG task graphs with parallel waves, and append-only replayable traces. See [docs/agentic_harness_orchestration.md](docs/agentic_harness_orchestration.md).
- **Autonomous Mission Planner**: Decomposes complex multi-step goals into verifiable sub-steps with automatic replanning and state rollback on failure.
- **FastMCP Tool Kernel**: Strict permission tiers (`SAFE`, `CONFIRM`, `RESTRICTED`) ensuring side-effect actions cannot bypass confirmation gates.
- **Multi-Provider LLM Gateway**: Local offline-first inference via Ollama (`qwen2.5-coder`, `deepseek-coder`) with intelligent cloud failover to OpenRouter.
- **Cognitive Memory & Vector RAG**: Episodic session memory, long-term SQLite persistence, and semantic vector retrieval.
- **Desktop & Screen Perception**: Native screen understanding, OCR, active window control, and system health telemetry.
- **Self-Healing & Reliability**: Autonomous code healer, thermal governor, and circuit-breaker isolation.

---

## 🚀 Quick Start

### 1. Installation
```bash
# Clone the repository
git clone https://github.com/vangaramcharan2007-del/alfred.git
cd alfred

# Install core dependencies
pip install -r requirements.txt
```

### 2. Launch Alfred Runtime
```bash
# Start interactive Alfred OS
python -m jarvisx

# Or run with the root launcher
python main.py
```

### 3. Available Commands
```bash
python -m jarvisx briefing      # Daily engineering and contextual briefing
python -m jarvisx daemon --start # Launch background sentinel daemon
python -m jarvisx report         # Generate productivity and system report
python -m jarvisx help           # View all available CLI operations
```

---

## 🧪 Testing

Run the test suite:
```bash
# Run unit tests
pytest tests/unit/test_tool_kernel.py -v

# Run full acceptance matrix
pytest tests/unit/ -v
```

---

## 📂 Project Organization

```text
src/jarvisx/
  ├── agentic/           # Agentic harness orchestration (backends, sandbox,
  │                      #   harness, verifier, planner, graph, scheduler)
  ├── automation/        # Desktop control, watchers, system tray, voice runtime
  ├── agents/            # Specialist agent implementations and loop runners
  ├── brain/             # Intent analysis, routing, and context synthesis
  ├── engineering/       # Autonomous code healer, debug loop, project intelligence
  ├── kernel/            # PersonalOSKernel, runtime lifecycle, and event bus
  ├── llm/               # LLM router, provider scoring, and Ollama integration
  ├── memory/            # Episodic memory, vector RAG, and state persistence
  ├── missions/          # Unified mission planner, failure classification, checkpointing
  ├── reliability/       # Circuit breaker, watchdog guard, autonomic sentinel
  └── tools/             # Builtin tools, FastMCP registry, and permission gateway
tests/                   # Unit, integration, and security verification tests
config/                  # System YAML configurations and provider settings
```

---

## 🧠 ADHD Mode: `alfred`

One command runs all four senses at once — it **talks, listens, watches and
does** — over a single shared task list.

```bash
python -m jarvisx.agentic alfred                  # mic + speakers + screen watching
python -m jarvisx.agentic alfred --text           # typed, no audio or desktop needed
python -m jarvisx.agentic alfred --energy low     # only offer tiny tasks today
```

It tells you honestly what came up rather than pretending:

```
  ears      keyboard
  mouth     text
  eyes      sensor
  hands     off (say build/write/fix)
```

The bottleneck is starting, not capacity. So Alfred picks by **energy, not
importance** — on a low-energy day you get a 5-minute task, never the scary
45-minute one. And a comma-separated brain dump becomes several small tasks,
because "write the assignment, pay the bill, call mom" as one 45-minute blob is
exactly the thing you will not start.

```bash
python -m jarvisx.agentic next --dump "everything on your mind, all at once"
python -m jarvisx.agentic talk --energy low          # talk/listen only
python -m jarvisx.agentic watch --task "the OS assignment"   # watch only
```

```
Captured 4 things
  [task    ] ~ 45m  Write the OS assignment its due today
  [task    ] ~  5m  Reply to that email from the professor
  [worry   ] ~ 20m  I'm worried about failing
  [delegate] ~ 20m  Someone should fix the printer

not yours: I'm worried about failing, Someone should fix the printer

DO THIS NEXT: Reply to that email from the professor  (~5m)
  1. Open the thread and write the first sentence
  2. Do one small piece and stop.
```

Worries, ideas and other people's problems are taken **out** of your queue, not
added to it. State persists to `var/agentic/intake.json`.

### 🎭 Give it a voice, and hands

```bash
python -m jarvisx.agentic alfred --persona stark    # Tony Stark, calls you "kid"
python -m jarvisx.agentic alfred --persona friday   # F.R.I.D.A.Y., calls you "Boss"
python -m jarvisx.agentic alfred --physical         # open apps, run gated commands
```

```
you> alfred> One thing. Pay the bill. 5 minutes, then you are done with it.
you> alfred> Good. That one is actually finished, not 'basically finished'.
you> alfred> Alright, kid. You have 3 open items, 2 of them actual tasks.
```

Two rules keep this from becoming a toy:

- **The persona never changes what you should do** — only how it sounds. If
  Stark could talk you out of a task, it would be a sarcastic procrastination
  engine. It is tested: the same brain dump picks the same task in every voice.
- **Physical reach is opt-in and gated.** `rm -rf /`, `format c:` and
  `shutdown` are refused *even when you say yes*. `sudo`, `git push` and
  `kill` ask first, and an unattended run always refuses rather than guessing.

### 📺 See it in a browser

```bash
python -m jarvisx.agentic serve      # open http://localhost:8123/
```

One big **"do this next"** card, an energy toggle that re-picks live, and a
dump box. It reads the same `var/agentic/intake.json` as the CLI, so the
browser, the terminal and your voice all show one list.

```
GET  /intake                      the list + next pick per energy level
POST /intake          {"dump": "everything on your mind"}
POST /intake/{id}/done            complete, and get the next one back
GET  /                            dashboard (Accept: text/html)
```

Worries and other people's problems are collected under **"not your
problem"** instead of sitting in the queue, because holding those is itself
the work.

`talk` wires the existing voice stack (`SecureVoiceGateway`, `FastSTTEngine`,
`RealTTSEngine`) to the orchestrator. Audio is optional — with no mic, speaker
or model it still runs end to end on text. Only an explicit `build/write/fix`
runs real agent work, and only with `--enable-agent`; everything else is
captured, because firing an agent at every sentence is how you get nine
half-finished automations.

---

## 🤖 Agentic Harness Orchestration

```python
from jarvisx.agentic import run_goal

report = run_goal("Build a CSV deduplicator with tests")
print(report.ok, report.succeeded)
print(report.final_output())
```

```bash
cp .env.example .env && python -m jarvisx.agentic doctor   # <- start here
python -m jarvisx.agentic plan "Build a CSV deduplicator with tests"
python -m jarvisx.agentic run  "Build a CSV deduplicator with tests"
python -m jarvisx.agentic serve --port 8123     # HTTP control plane + SSE events
python demo_agentic_harness.py                  # live end-to-end demonstration
```

`doctor` verifies your API key, backend selection, a live model round-trip,
native tool calling and the sandbox, then exits `1` if you cannot run yet.

**Without a model key the agents fall back to an offline heuristic that writes
a placeholder file, not real code.** Add `GROQ_API_KEY` (or
`OPENROUTER_API_KEY`, or `OLLAMA_BASE_URL`) to `.env` — it is loaded
automatically, no `python-dotenv` needed.

---

## 📜 License
MIT License — Sovereign and autonomous personal AI assistant.
