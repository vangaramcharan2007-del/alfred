# Jarvis X

An offline-first, modular personal AI operating system scaffold.

Jarvis X (Alpha 0.1) provides a robust "One Alfred" architecture designed to route tasks seamlessly across multiple domains (device control, intelligence, memory, workflow) using the OmniRoute LLM gateway and a unified Event Bus (Hermes). 

> **Phase Ω (Production Ready)**
> Jarvis X is designed to be a "clone, install, run" repository. No extensive configuration required.

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/your-username/project-jarvis-x.git
cd project-jarvis-x
```

### 2. Install
Run the automated bootstrap script. This will create your virtual environment, install dependencies, and create standard project directories.
```bash
# On Windows PowerShell
.\install.ps1

# On Linux/macOS
./install.sh
# or
make install
```

### 3. Run
Boot the Jarvis X operating system.
```bash
# On Windows PowerShell
.\run.ps1

# On Linux/macOS
./run.sh
# or
make run
```

## 🛠️ Testing & Diagnostics

**Diagnose System Health:**
Jarvis X includes a diagnostic script to verify your Python environment, required dependencies, and local Ollama connections:
```bash
make diagnose
```

**Run Acceptance Tests:**
To verify the core orchestration path is fully functional, run the smoke test:
```bash
python scripts/acceptance_test.py
```

**Run Full Test Suite:**
```bash
# On Windows PowerShell
.\test.ps1

# On Linux/macOS
./test.sh
# or
make test
```

## 🏗️ Architecture Overview

The system operates via a strict verified control path:

```text
User
 ↓
Alfred (Central Orchestrator)
 ↓
Mission Engine (Task Planning & Delegation)
 ↓
Capability Intelligence & Skill Ranker
 ↓
Skill Executor
 ↓
Tool Registry (Dynamic Plugin Discovery)
 ↓
Execution
 ↓
Memory + Workflow Learning
```

## 📦 Directory Structure

- `src/jarvisx/` - Core source code (Agents, Core Services, Skills, Tools)
- `tests/` - Comprehensive test suite
- `scripts/` - Utility scripts (`bootstrap.py`, `diagnose.py`, `acceptance_test.py`)
- `examples/` - Reference implementations and valid demos
- `docs/` - System architecture and reports

## 🤝 Contributing
- Ensure PRs pass all tests (`make test`).
- Target >95% test coverage for `src/jarvisx/`.

## 📜 License
MIT License
