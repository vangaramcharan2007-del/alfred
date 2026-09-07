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

## 📜 License
MIT License — Sovereign and autonomous personal AI assistant.
