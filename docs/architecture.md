# Jarvis X Architecture & Governance Specification (`docs/ARCHITECTURE.md`)

This document defines the official 6-layer structural constitution of Jarvis X, established during **Phase 44B: Jarvis X Architectural Constitution**.

---

## 1. Core Implementation Principles
1. **Do NOT move folders** without proven architectural need.
2. **Do NOT rewrite working modules** or break established import relationships.
3. **Contracts before features; Architecture before automation.**
4. Eliminate unnecessary abstractions and avoid speculative or unverified agents/UI demonstrations.

---

## 2. The 6-Layer Hierarchy

```
1. Human Layer         (User guidance & config)
          ↓
2. Intelligence Layer  (Alfred central orchestration & decision making)
          ↓
3. Agent Layer         (Specialized autonomous workers: Brain, Memory, Planner, Voice, Vision, Hands, Research)
          ↓
4. Capability Layer    (Reusable modular abilities & tools exposed to agents)
          ↓
5. Infrastructure Layer(External systems, adapters, database persistence, observability)
          ↓
6. Interface Layer     (Human-facing interaction surfaces & command displays)
```

### Layer Details & Module Ownership

* **Layer 1 — Human Layer:** Holds user preferences, operational parameters, and configuration settings.
  * *Canonical modules:* `config/`
* **Layer 2 — Alfred Intelligence Layer:** Centralized routing engine, lifecycle supervisor, mission decision maker, and architectural governance.
  * *Canonical modules:* `main.py`, `core/`, `kernel/`, `runtime/`, `decision/`, `evolution/`, `architecture/`
* **Layer 3 — Agent Layer:** Encapsulates autonomous functional domains controlled by Alfred.
  * *Canonical modules:* `brain/`, `cognition/`, `memory/`, `missions/`, `engineering/`, `llm/`, `learning/`, `automation/`, `skills/`, `verification/`
* **Layer 4 — Capability Layer:** Reusable operational tools and benchmark suites made accessible to active agents.
  * *Canonical modules:* `capabilities/`, `tools/`, `benchmark/`
* **Layer 5 — Infrastructure Layer:** Manages persistent storage connectors, deployment wrappers, LLM models, and observability logging.
  * *Canonical modules:* `adapters/`, `deployment/`, `observability/`, `models/`
* **Layer 6 — Interface Layer:** Handles command line presentations, input argument parsing, and user terminal interfaces.
  * *Canonical modules:* `interface/`, `ui/`

---

## 3. Dependency Flow & Forbidden Interactions
Dependencies flow strictly **downward** from Human $\rightarrow$ Alfred $\rightarrow$ Agents $\rightarrow$ Capabilities $\rightarrow$ Infrastructure, while Interface components may invoke Alfred and Agent APIs to fulfill human command execution.

### Explicit Forbidden Imports
To safeguard modular integrity and prevent architectural regressions, the following import relationships are strictly restricted via AST enforcement (`ArchitectureValidator`):
1. **`memory` $\rightarrow$ `runtime`**: Memory storage must remain decoupled from higher-level runtime engine sequencing.
2. **`automation` $\rightarrow$ `brain`**: Physical input/output action layers must not couple directly to core reasoning logic.
3. **`tools` $\rightarrow$ `missions`**: Low-level tool utilities must remain agnostic to mission planning abstractions.
4. **`adapters` $\rightarrow$ `ui` / `interface`**: Backend persistence and database connectors must never import presentation surfaces.

---

## 4. The Canonical Agent Interface (`AgentContract`)
Any functional autonomous worker introduced into Jarvis X must inherit from `jarvisx.architecture.AgentContract` and implement the standard operational interface:
* **Attributes:** `name: str`, `purpose: str`, `capabilities: List[str]`
* **Methods:**
  * `execute(task: Dict[str, Any], **kwargs: Any) -> Dict[str, Any]`
  * `status() -> Dict[str, Any]`
  * `report() -> str`

---

## 5. Architectural Verification & Enforcement
Automated verification is embedded within the build pipeline via `jarvisx.architecture.dependency_rules.ArchitectureValidator`. It scans the AST of all source files to guarantee zero circular dependencies, zero layer inversions, and strict adherence to defined package boundaries.
