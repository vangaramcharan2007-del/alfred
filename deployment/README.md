# Jarvis X — Production Deployment & Runtime Operations Guide

This directory contains the automated deployment, lifecycle control, and health monitoring scripts for **Jarvis X Sovereign Personal OS**.

---

## 🏛️ Deployment Architecture & Lifecycle

```text
                            WINDOWS WORKSTATION
                                     │
                 ┌───────────────────┴───────────────────┐
                 ▼                                       ▼
        [1. INSTALLATION]                       [2. FIRST-BOOT FLOW]
     .\deployment\install.ps1                .\deployment\start_jarvis.ps1
     • Verify Python >= 3.11                 • Init SQLite Database Schemas
     • Check Package Dependencies            • Start Background Daemon (PID)
     • Create var/ & config/ paths           • Bind High-Speed IPC Gateway
     • Generate Startup Scripts              • Transition State: READY
                 │                                       │
                 └───────────────────┬───────────────────┘
                                     ▼
                          [3. HEALTH & DIAGNOSTICS]
                         .\deployment\health_check.ps1
                         • PRAGMA Integrity Checks
                         • Loopback IPC Latency (< 2ms)
                         • Memory & Resource Bounds
                                     │
                                     ▼
                          [4. GRACEFUL SHUTDOWN]
                          .\deployment\stop_jarvis.ps1
                          • IPC Shutdown Signal
                          • Release Atomic PID Lockfile
```

---

## 📋 System Requirements

* **Operating System**: Windows 10/11 (64-bit) or Windows Server
* **Python**: Version **3.11+** installed and available in `PATH`
* **RAM**: 4GB minimum (Jarvis X idle background daemon consumes **< 60MB RAM**)
* **Disk Space**: 500MB free space for databases, logs, and Obsidian vault index

---

## 🚀 Quickstart Deployment

### 1. Run First-Time Installation
```powershell
# Open PowerShell in repository root and run:
.\deployment\install.ps1
```
*Checks Python 3.11+, validates core dependencies, creates runtime directories, initializes configuration, and generates startup scripts.*

### 2. Launch Background Daemon
```powershell
.\deployment\start_jarvis.ps1
```
*Starts the persistent sovereign daemon in the background and verifies IPC connectivity on `127.0.0.1:10404`.*

### 3. Run Health Diagnostics
```powershell
.\deployment\health_check.ps1
```
*Executes full diagnostic suite covering Python, packages, SQLite databases, config, and IPC responsiveness.*

### 4. Stop Background Daemon
```powershell
.\deployment\stop_jarvis.ps1
```
*Sends graceful shutdown command via IPC socket and releases the PID lock.*

---

## 📁 Runtime Directory Hierarchy

```text
project-jarvis-x/
├── config/
│   └── jarvis.yaml              # Primary system configuration file
├── var/
│   ├── db/                      # Persistent SQLite Databases
│   │   ├── knowledge.db         # Obsidian vault document & chunk index
│   │   ├── memory_intelligence.db # Episodic, semantic, procedural memory & relations
│   │   ├── evaluation.db        # Evidence tracing & response quality scores
│   │   ├── operating_loop.db    # Academic coach syllabus & 8-stage loop telemetry
│   │   └── reliability.db       # System health metrics & crash recovery logs
│   ├── runtime/
│   │   ├── jarvisd.pid          # Atomic process ID lockfile
│   │   └── state.json           # Real-time daemon presence & resource telemetry
│   ├── logs/
│   │   └── daemon.log           # Daemon background execution log
│   ├── backups/                 # Point-in-time database snapshots
│   └── scripts/                 # Windows startup .bat / .ps1 / Task XML
└── deployment/
    ├── install.ps1              # First-boot environment setup & dependency installer
    ├── start_jarvis.ps1         # Daemon background service launcher
    ├── stop_jarvis.ps1          # Daemon graceful shutdown controller
    ├── health_check.ps1         # Comprehensive system diagnostic inspector
    └── README.md                # Deployment documentation
```

---

## 💻 Interactive & CLI Usage

Once installed, use the unified CLI to communicate directly with the warm daemon:

```powershell
# Interactive Alfred Shell
python -m jarvisx

# Direct CLI Query via High-Speed IPC
python -m jarvisx alfred "prepare my binary tree revision notes"

# Academic & 10 CGPA Coach Commands
python -m jarvisx coach status
python -m jarvisx coach plan
python -m jarvisx coach topic "Graph Algorithms" 0.10

# Autonomous Operating Loop Trigger
python -m jarvisx loop run
python -m jarvisx loop status

# Daemon Control
python -m jarvisx daemon status
python -m jarvisx daemon ping
python -m jarvisx daemon brief
```
