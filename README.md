# Alfred & Friday — Autonomous Engineering & Academic Operating System

An offline-first, production-polished autonomous AI system consisting of **Alfred** (Engineering & Desktop Automation Butler) and **Friday** (10 CGPA Academic & Life Executive Assistant).

---

## 🌟 Features

### 🎩 Alfred — Engineering & Desktop Automation
- **Workspace Recovery (`continue`)**: Scans git status, active branch, commits, TODOs, and test suite health.
- **Automated Bug Fixing (`fix this`)**: Reads test failures, inspects diffs/files, interacts with local LLM, applies fix, and verifies.
- **Code Intelligence**: Generate unit tests (`write tests`), architectural explanations (`explain`), code reviews (`review`), dead code scans (`find dead code`), and Google-style docstrings (`generate docs`).
- **Real Desktop Actions**: 
  - File organization (`organize`) by categories (Images, Docs, Code, etc.)
  - Folder compression (`compress`)
  - Screen capture (`screenshot`)
  - Running window list (`windows`)
  - Process termination (`kill`)
  - Disk usage analysis (`disk`)
- **Autonomous Missions (`mission <request>`)**: Synthesizes python modules, writes unit tests, executes pytest verification, and initializes local Git repositories.

### ♀️ Friday — Executive Academic Assistant (10 CGPA Engine)
- **Academic War Mode (`war`)**: Generates weighted impact scores across registered courses based on syllabus coverage, current grade, and credit weights to maximize CGPA.
- **Daily Dashboard (`python -m friday`)**: Visualizes class schedules, assignment countdowns, study session progress, habit streaks, health recommendations, and exam readiness verdicts.
- **Time Saved Tracking (`report`)**: Logs real task automations, minutes saved, and click reductions to `TIME_SAVED_REPORT.md`.

---

## 🛠️ Quick Start

```bash
# 1. Install dependencies
pip install -e .

# 2. Run System Health Check
python -m jarvisx doctor

# 3. View Available Commands
python -m jarvisx help

# 4. Run Academic War Mode
python -m jarvisx war

# 5. Run Workspace Continuation
python -m jarvisx continue

# 6. Launch Friday Daily Dashboard
python -m friday
```

---

## 🧪 Verification & Testing

Run the full verified production test suite:
```bash
python -m pytest tests/unit/ -v
```
