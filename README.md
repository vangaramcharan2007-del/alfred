# Jarvis X Autonomous AI Assistant & Engineering Operating System

[![Build Status](https://img.shields.io/badge/status-production--ready-brightgreen.svg)]()
[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)]()
[![Phase](https://img.shields.io/badge/phase-39%20(Production%20Maturity)-purple.svg)]()

Jarvis X is an autonomous engineering operating system and local AI assistant. It combines Intent Analysis, Architecture Planning, LLM Model Routing, Real Disk Workspace Generation, Automated Pytest Sandbox Execution, Local Git Management, and Cognitive Memory Storage into a unified runtime kernel.

---

## 🏗️ Architecture Matrix

```
                      +-----------------------------------+
                      |      Jarvis CLI / Main Entry      |
                      +-----------------------------------+
                                        |
                      +-----------------------------------+
                      |       Runtime Kernel Services     |
                      +-----------------------------------+
                                        |
             +--------------------------+--------------------------+
             |                          |                          |
    +------------------+      +-------------------+      +------------------+
    | Brain Controller |      | Mission Executor  |      | Decision Engine  |
    +------------------+      +-------------------+      +------------------+
             |                          |                          |
             +--------------------------+--------------------------+
                                        |
             +--------------------------+--------------------------+
             |                          |                          |
    +------------------+      +-------------------+      +------------------+
    | Capability Reg.  |      | Provider Selector |      | Memory & Graph   |
    +------------------+      +-------------------+      +------------------+
```

---

## 🚀 Quick Start

### 1. Installation & Environment Setup
```bash
# Clone repository
git clone https://github.com/vangaramcharan2007-del/alfred.git
cd alfred

# Install dependencies
pip install -r requirements.txt
```

### 2. Run Main Production Runtime
```bash
python -m jarvisx
```

**Output**:
```text
=========================
       JARVIS X
=========================

Memory          ........ ONLINE
LLM Gateway     ........ ONLINE
Capabilities    ........ ONLINE
Agents          ........ ONLINE
Git             ........ ONLINE

Alfred online.
```

### 3. Run Golden Production Mission
Execute a real autonomous mission ("Build a personal productivity dashboard"):
```bash
python scripts/run_real_mission.py
```

This runs the full end-to-end pipeline with real file generation in `jarvis_workspace/`, real pytest sandbox execution, real local git commits, and memory storage.

---

## 🧪 Testing

Run the full structured test suite (Unit, Integration, System):
```bash
pytest tests/unit/ tests/integration/ tests/system/ tests/
```

---

## 📂 Project Organization

```text
src/jarvisx/             # Core Jarvis X Operating System Source
  ├── runtime/           # Bootstrap, Shutdown, State, Runtime Services
  ├── kernel/            # Kernel Lifecycle, Event Orchestrator, Health Coordinator
  ├── brain/             # Intent Understanding, Mission Router, Context Manager
  ├── decision/          # Unified Decision Engine & Explainer
  ├── missions/          # Autonomous Mission Manager & Executor
  ├── meta/              # System Knowledge Graph & Meta Memory
  ├── llm/               # LLM Gateway & Provider Scoring
  ├── providers/         # Intelligence & Selection Services
  ├── interface/         # CLI & Voice Runtime Engine
  └── main.py            # Single Production Entry Point

scripts/                 # Utility Scripts
  └── run_real_mission.py # Single Golden Production Mission Script

examples/
  └── phase_history/     # Archived Phase Demonstration Scripts

config/
  └── jarvis.yaml        # Main Consolidated System Configuration

docs/
  └── ARCHITECTURE_AUDIT.md # Architecture Audit & Production Readiness Score
```

---

## ⚠️ Current Limitations & Fallback Behavior

1. **GitHub Cloud Integration**: If `GITHUB_TOKEN` is not configured in the environment, GitHub PR creation returns an explicit `NOT_AVAILABLE` status contract instead of returning a simulated response.
2. **Local LLM Models**: Offline model routing defaults to local Ollama (`qwen2.5-coder:7b`, `deepseek-coder:6.7b`). If Ollama is offline, local intelligent routing fallbacks engage automatically.

---

## 📜 License
MIT License
