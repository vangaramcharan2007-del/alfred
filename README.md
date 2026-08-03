# Jarvis X - Autonomous AI Assistant & Engineering OS

Jarvis X is an autonomous engineering assistant and persistent desktop AI system capable of dynamic reasoning, workspace file generation, automated sandbox testing, version control commits, and multimodal interaction.

---

## 🚀 What Jarvis X Can Actually Do Now

- **Autonomous Engineering Missions**: Executes real coding tasks (Python REST APIs, Calculator CLIs, Repository Analysis, Documentation Generation, Module Refactoring, and Bug Fixing).
- **Disk File Generation**: Writes modular project files directly to disk under `jarvis_workspace/<mission_id>/` and `workspace/<mission_id>/`.
- **Pytest Sandbox Verification**: Executes real `pytest` sub-processes against generated project code to verify pass/fail status.
- **Local Git Control**: Performs real `git init`, `git add`, and `git commit` operations locally.
- **SQLite Data Persistence**: Stores all mission histories, step execution timelines, token usage, and failure tracebacks in `var/db/missions.db`, `executions.db`, and `failures.db`.
- **Dynamic Reasoning & Trust Engine**: Analyzes requirements, calculates confidence scores (e.g. 94%), evaluates risk levels (`LOW`, `MEDIUM`, `HIGH`), and enforces human approval gates.
- **Multimodal Desktop Assistant**: Supports wake-word detection ("Alfred"), active window context vision, speech input/output, and Alfred persona responses.
- **Zero Simulation Policy**: Returns explicit `NOT_AVAILABLE` status contracts when external services (e.g., local Ollama daemon or GitHub cloud API token) are offline or unconfigured.

---

## 🛠️ Installation & Setup

```bash
# 1. Clone workspace
git clone https://github.com/vangaramcharan2007-del/alfred.git
cd alfred

# 2. Setup Virtual Environment & Install Dependencies
python -m venv .venv
.venv\Scripts\activate  # On Windows
pip install -r requirements.txt
pip install pytest pytest-asyncio pyyaml fastapi httpx pyttsx3
```

---

## 💻 Running Alfred

```bash
# System Diagnostic Check
python scripts/reality_check.py

# Launch Production CLI
python -m jarvisx

# System Status
python -m jarvisx status

# Generate Dynamic Execution Plan (Without Execution)
python -m jarvisx plan "Build a weather CLI application"

# Execute Autonomous Mission
python -m jarvisx mission "Build a weather CLI application"

# View Persisted Mission History
python -m jarvisx history

# Explain Decision Rationales
python -m jarvisx explain mission_<id>

# Replay Previous Mission State
python -m jarvisx replay mission_<id>

# Multimodal Desktop Assistant Mode
python -m jarvisx assistant
```

---

## 📌 Supported Capabilities

| Capability | Integration Engine | Fallback / Contract |
| :--- | :--- | :--- |
| **Code Generation** | Dynamic Architecture Agent & Goose | Local workspace generator |
| **Testing** | Sandbox Pytest Runner | Static syntax pass verification |
| **Version Control** | Local Git Binary | `NOT_AVAILABLE` if `git` missing |
| **LLM Provider** | Ollama (`localhost:11434`) | `NOT_AVAILABLE` if Ollama offline |
| **Voice Interface** | pyttsx3 TTS / Speech Capture | Stdout text stream fallback |
| **Desktop Vision** | Desktop Context Detector | Active window title scan |

---

## ⚠️ Current Limitations

1. **Remote Cloud GitHub PRs**: Requires setting `GITHUB_TOKEN` in the environment; otherwise returns explicit `NOT_AVAILABLE`.
2. **Local LLM Daemon**: Connects to `http://localhost:11434/api/generate` when Ollama is running. Returns `NOT_AVAILABLE` when offline.

---

## 🗺️ System Roadmap

- [x] Phase 39: Production Maturity Refactor
- [x] Phase 40: Real Mission Execution & Verification
- [x] Phase 41: Trust Layer & Dynamic Reasoning Engine
- [x] Phase 42: Multimodal Human Presence Layer
- [x] Phase 43: Usability & Integration Hardening
- [ ] Phase 44: Multi-Agent Parallel Mesh Execution
