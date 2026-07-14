# JarvisX Architecture Matrix

## Core Subsystems
1. **Agent Forge (`agent_forge.py`)**: Dynamically spawns ephemeral Python sub-agents inside a sandbox with 30s timeouts. Agents publish via the local event bus.
2. **Master Supervisor (`supervisor.py`)**: Monitors subsystem threads with exponential backoff restarts for failure domains.
3. **Ouroboros Daemon (`ouroboros_daemon.py`)**: Central async `gather` loop that decouples module execution, ensuring offline queues and system state loops don't freeze the host.
4. **Message Bus (`message_bus.py`)**: Asynchronous pub/sub event bus replacing hard-coupled function calls.

## Tool Layers
- **Sandbox Exec (`sandbox_exec.py`)**: Python `subprocess` isolated runtime enforcing resource limits and auto-deleting temp files.
- **Semantic Memory (`semantic_memory.py`)**: `aiofiles` integrated SQLite structural vector index using cosine similarity matching.
- **Git Sync (`git_sync.py`)**: Native subprocess binding array replacing shell tokens.
- **Gesture Macros (`gesture_macros.py`)**: Vision intercept layer featuring 1.5s frame debouncing and low-priority throttled loops for OS window manipulation.
- **Webhook Sentinel (`webhook_sentinel.py`)**: `httpx` async wrapper with local SQLite offline queuing.

---

## System Health & Bottlenecks (Audit_Agent Append)
### Identified Race Conditions:
- **Message Bus Queue Extraction**: The SQLite queues (used in Webhook Sentinel and Git Sync) do not presently enforce row-level locking or semaphore gates. Concurrent agents publishing rapidly could cause database locking errors (`database is locked`).
- **Sandbox File Collisions**: The sandbox uses `tempfile.mkstemp` safely, but concurrent `AgentForge` writes to `src/jarvisx/agents/agent_{uuid}.py` may bottleneck if UUIDs clash or if the OS enforces strict directory locks during heavy swarm spawning.
### Resource Leaks:
- **Thread Exhaustion**: Uncapped daemon loops generating infinite subprocesses could exceed the Windows Handle limit if `sandbox_exec.py` timeouts fail to forcefully `taskkill` zombied PIDs.
### Optimization Mandate:
- Implement `asyncio.Semaphore` on all SQLite connection scopes.
- Add `subprocess.run` `creationflags` to ensure child processes are fully detached or grouped to a Job Object in Windows to guarantee true termination.
