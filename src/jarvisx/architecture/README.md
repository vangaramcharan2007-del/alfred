# Jarvis X Architectural Constitution (`src/jarvisx/architecture`)

This module enforces the **Phase 44B Architectural Constitution** across the Jarvis X codebase without physically relocating existing production directories or disrupting validated import paths.

## Purpose & Core Philosophy
* **Delete before creating.**
* **Merge before extending.**
* **Contracts before features.**
* **Architecture before automation.**

We enforce architectural boundaries via static validation and interface contracts rather than physical folder migrations.

## Key Components

1. **`layers.py`**: Exports `LAYER_REGISTRY`, a canonical mapping of all 27 top-level `src/jarvisx` packages to their respective architectural layers (Human, Alfred, Agents, Capabilities, Infrastructure, Interface).
2. **`contracts.py`**:
   * **`ArchitectureContract`**: Governs allowable dependency flow (top-down) and explicit forbidden package interactions (e.g., memory $\rightarrow$ runtime, database $\rightarrow$ UI).
   * **`AgentContract`**: Canonical abstract base class defining the mandatory interface for all autonomous workers (`name`, `purpose`, `capabilities`, `execute()`, `status()`, `report()`).
3. **`dependency_rules.py`**: Exports `ArchitectureValidator`, an AST-powered validation engine that performs static repository inspections to uncover import cycles, forbidden pairings, and layer inversions.
