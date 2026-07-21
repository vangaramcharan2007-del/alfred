# Phase 23: Persistent Objective & Background Execution Engine

## Overview

Jarvis X's execution model has been upgraded from an in-memory, synchronous process to a **durable, persistent background execution engine**. This ensures that Jarvis X can survive interruptions—such as crashes, restarts, and pauses—without losing its objectives or execution progress.

## Architecture & Components

The Persistent Objective Engine introduces several key components:

### 1. SQLite-Backed Persistent Queue
- Replaced the in-memory queue with `PersistentQueue` (`persistent_queue.py`).
- Objectives are stored in an `objectives` table with fields for status, priority, and progress tracking.
- Supports querying by status (e.g., fetching only `QUEUED` objectives for the background worker).
- **Concurrency-Safe:** Enforces standard priority scheduling across threads or restarts.

### 2. Checkpoint Manager
- Integrated `CheckpointManager` (`checkpoint_manager.py`) directly into the `TaskExecutor`.
- Tracks the `current_step_index` dynamically.
- Automatically saves execution snapshots to a `checkpoints` table in the SQLite database upon the completion of each step.

### 3. Objective State Machine
- Strict state enforcement using `ObjectiveStateMachine` (`objective_state_machine.py`).
- Supported states: `QUEUED`, `RUNNING`, `PAUSED`, `COMPLETED`, `FAILED`, `CANCELLED`.
- Provides explicit transition validation rules to prevent out-of-order execution states.

### 4. Background Worker & Dispatcher
- The `BackgroundWorker` (`background_worker.py`) runs on an independent thread, polling the `PersistentQueue` for pending (`QUEUED`) objectives.
- Interacts with the `ExecutionDispatcher` to spin up `TaskExecutor` instances with full lifecycle event publishing.
- Listens for an internal stop event to perform a graceful shutdown.

### 5. Resume Engine
- Discovers `RUNNING` objectives left over from unexpected process crashes upon startup.
- The `ResumeEngine` (`resume_engine.py`) resets such aborted objectives back to `QUEUED` and requeues them automatically.
- Upon requeueing, the TaskExecutor queries the `CheckpointManager` and automatically **fast-forwards** to the last completed step instead of starting over.

### 6. Objective Scheduler
- Facilitates deferred objective execution (`objective_scheduler.py`).
- Temporarily stores time-delayed tasks using a background thread and enqueues them to the `PersistentQueue` once their scheduled time elapses.

## Real-World Validation

The implementation was robustly tested against physical file operations (`demo_phase23.py`):
1. **Crash Recovery:** Demonstrated pausing the background worker forcibly while an objective was half-finished, restarting the system, and validating that the objective resumed flawlessly from its exact point of interruption without duplicating previous files.
2. **Pause / Resume:** Proved the capability to manually transition an objective to `PAUSED`, observing static filesystem activity, and subsequently resuming to `COMPLETED`.
3. **Queue Persistence:** Verified objective data structures are reliably serialized and recovered post-shutdown.
4. **Priority Queue:** Confirmed that CRITICAL objectives are executed ahead of NORMAL and LOW ones regardless of enqueue order.
5. **State Machine Integrity:** Enforced correct logical flows, ensuring an objective cannot jump from `PAUSED` to `COMPLETED` without running.

## Conclusion

Jarvis X is no longer a fragile runtime. It operates as a resilient **Digital Butler**, maintaining state durability, pausing seamlessly, and recovering intelligently across process restarts.
