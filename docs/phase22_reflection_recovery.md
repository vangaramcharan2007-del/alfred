# Phase 22: Reflection & Recovery Engine

## Overview
Phase 22 transforms Jarvis X from a simple execution engine into an autonomous, self-recovering system. The new architecture intercepts failures (like missing applications or permission errors) and attempts alternative strategies before terminating the objective.

## Architecture Diagram
```mermaid
graph TD
    A[TaskExecutor] -->|Step| B[ExecutionCoordinator]
    B -->|Execute| C[Subsystem (OS, Browser)]
    B -->|Verify| D[ActionVerifier]
    C --> B
    D --> B
    B -->|Reflect| E[ReflectionEngine]
    E -->|Classify| F[FailureClassifier]
    F --> E
    E -->|ReflectionResult| B
    B -->|Recover| G[RecoveryPlanner]
    G -->|Query| H[CapabilityRegistry]
    G -->|Strategy| B
    B -->|Event| I[EventBus]
```

## Core Modules

### 1. Event Bus (`event_bus.py`)
A lightweight publish/subscribe pattern decoupled from the execution flow. Modules (like logging or future agents) subscribe to `ExecutionEvent` (e.g., `STEP_STARTED`, `RECOVERY_STARTED`).

### 2. Execution Context (`execution_context.py`)
Provides dynamic path resolution. Instead of hardcoding `C:/Users/.../Desktop`, the planner issues commands to `${DESKTOP}`. `ExecutionContext` resolves this based on the host OS. Supports `${HOME}`, `${DESKTOP}`, `${DOWNLOADS}`, `${TEMP}`, etc.

### 3. Capability Registry (`capability_registry.py`)
Stores metadata about tools (e.g., `chrome` has alternatives `edge` and `firefox`). Crucially, it does not scan the system at startup—it waits for a tool to fail during execution before relying on the registry to supply an alternative to the recovery planner.

### 4. Failure Classifier (`failure_classifier.py`)
Converts raw Exceptions and verification booleans into structured `FailureCategory` enums (e.g., `MISSING_APPLICATION`, `PERMISSION_DENIED`).

### 5. Reflection Engine (`reflection_engine.py`)
Takes execution outcomes and classifications to build a `ReflectionResult`. Evaluates if the failure is recoverable, computes confidence, and outputs a recommendation string (e.g., `"alternative_tool"`).

### 6. Recovery Planner (`recovery_planner.py`)
Implements the Strategy Pattern. Translates the recommendation from `ReflectionResult` into actionable changes:
- `AlternativeToolStrategy`: Looks up fallback tools in the Capability Registry.
- `PermissionRecoveryStrategy`: Falls back to a safe writable directory (e.g., `$TEMP`).
- `RetryStrategy`: Retries transient failures up to `max_retries`.
- `AbortStrategy`: Terminates unrecoverable steps.

### 7. Execution Coordinator (`execution_coordinator.py`)
Isolates the complex `Execute -> Verify -> Reflect -> Recover` loop from the `TaskExecutor`.

## Recovery Flow Example
1. `TaskExecutor` asks `ExecutionCoordinator` to run step: "Open chrome".
2. `AppLauncher` fails because Chrome isn't installed. Returns `FileNotFoundError`.
3. `FailureClassifier` receives the error and classifies as `MISSING_APPLICATION`.
4. `ReflectionEngine` outputs `ReflectionResult(recoverable=True, recommendation="alternative_tool")`.
5. `RecoveryPlanner` passes the context to `AlternativeToolStrategy`.
6. Strategy asks `CapabilityRegistry` for alternatives to "chrome" -> returns `["edge", "firefox"]`.
7. Strategy modifies the step target to "edge" and re-executes.
8. `ExecutionCoordinator` verifies Edge opens and returns `True` to `TaskExecutor`.

## Extension Guide
- **Adding a Capability**: Instantiate `Capability(name, alternatives=[...])` and pass to `CapabilityRegistry.register()`.
- **Adding a Strategy**: Inherit from `RecoveryStrategy`, implement `can_handle()` and `recover()`, and register it in `RecoveryPlanner`.
- **Listening to Events**: Run `event_bus.subscribe(ExecutionEvent.STEP_COMPLETED, my_callback)`.

## Known Limitations
- The `PermissionRecoveryStrategy` currently just redirects to the OS temporary directory. Real implementations should dynamically prompt the user for an alternative path or check secondary partitions.
- Verification strategies remain simplistic (timing-based polling).

## Future Improvements (Phase 23)
- Real user-in-the-loop fallback via Voice: "I don't see Chrome. Would you like me to use Edge?"
- Capability auto-discovery upon agent idle time.
