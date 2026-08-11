# Jarvis X — Windows Installation Guide

## Prerequisites

| Requirement | Minimum | Verify |
|:---|:---|:---|
| **Windows** | 10 or 11 | — |
| **Python** | 3.11+ | `python --version` |
| **Git** | any | `git --version` |
| **pip** | bundled with Python | `pip --version` |

> Python 3.11 is required (`requires-python = ">=3.11"` in pyproject.toml).
> Download from https://www.python.org/downloads/ if needed.

## Installation

### 1. Clone the repository

```powershell
git clone https://github.com/vangaramcharan2007-del/alfred.git project-jarvis-x
cd project-jarvis-x
```

### 2. Create a virtual environment (recommended)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install Jarvis X in editable mode

```powershell
pip install -e .
```

This installs all runtime dependencies declared in `pyproject.toml`:
`aiofiles`, `aiohttp`, `cryptography`, `fastapi`, `httpx`, `numpy`,
`pandas`, `pydantic`, `PyYAML`, `requests`, `websockets`, `psutil`.

### 4. (Optional) Install development dependencies

```powershell
pip install -e ".[dev]"
```

### 5. (Optional) Install optional feature groups

```powershell
pip install -e ".[voice]"     # Speech recognition & TTS
pip install -e ".[vision]"    # OCR & computer vision
pip install -e ".[desktop]"   # Desktop automation
```

## Verification

### Smoke test (no pytest required)

```powershell
python scripts/smoke_test.py
```

All 13 checks should report `[PASS]`.

### System status

```powershell
python -m jarvisx status
```

### Help / available commands

```powershell
python -m jarvisx help
```

### Interactive mode

```powershell
python -m jarvisx
```

Type commands at the `alfred >` prompt. Type `exit` to quit.

## Daemon (background service)

### Start

```powershell
python -m jarvisx daemon --start
```

Or use the deployment script:

```powershell
powershell -ExecutionPolicy Bypass -File deployment\start_jarvis.ps1
```

### Check health

```powershell
python -m jarvisx daemon status
```

Or:

```powershell
powershell -ExecutionPolicy Bypass -File deployment\health_check.ps1
```

### Stop

```powershell
python -m jarvisx daemon --stop
```

Or:

```powershell
powershell -ExecutionPolicy Bypass -File deployment\stop_jarvis.ps1
```

## Directory Structure (auto-created at first run)

```
project-jarvis-x/
├── config/           # Configuration (jarvis.yaml)
├── logs/             # Application logs
├── var/
│   ├── db/           # SQLite databases
│   ├── runtime/      # PID lock, state files
│   ├── logs/         # Daemon logs
│   ├── backups/      # Backup storage
│   └── scripts/      # Generated scripts
└── src/jarvisx/      # Source code
```

All runtime directories are created automatically by `RuntimeKernel.__init__`
using relative paths. Always run Jarvis X from the repository root.

## Troubleshooting

| Problem | Fix |
|:---|:---|
| `ModuleNotFoundError` | Run `pip install -e .` from the repo root |
| Python version error | Upgrade to Python 3.11+ |
| Daemon won't start | Check if port 10404 is in use: `netstat -ano \| findstr 10404` |
| Config not found | Make sure you're running from the repo root directory |
