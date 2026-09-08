# Alfred Agentic Harness Orchestration

`src/jarvisx/agentic/` is a single coherent stack that turns a natural-language
goal into **verified, traced work**. It is the layer to build on when you want
Alfred to *do* multi-step engineering rather than match keywords.

```
        goal
          │
          ▼
   ┌─────────────┐   LLMPlanner (model-authored JSON plan)
   │   planner   │──▶ validated, repaired, or fallen back to heuristics
   └─────┬───────┘
         ▼
   ┌─────────────┐   DAG: ids, roles, depends_on, budgets, verify checks
   │    graph    │──▶ cycle / duplicate / dangling-dependency detection
   └─────┬───────┘
         ▼
   ┌─────────────┐   wave 1 ∥ wave 2 ∥ …  (independent nodes run in parallel)
   │  scheduler  │──▶ retries, failure propagation, usage roll-up, report
   └─────┬───────┘
         ▼  one AgentHarness per node
   ┌─────────────┐   think ─▶ act ─▶ observe, until done or budget breached
   │   harness   │──▶ loop guard, permission gate, token/step/wall budgets
   └─────┬───────┘
    ┌────┴─────┐
    ▼          ▼
 registry    verifier      both operate on…
    └────┬─────┘
         ▼
   ┌─────────────┐
   │   sandbox   │  jailed subprocess: rlimits, timeout, path jail, env scrub
   └─────────────┘

   everything above writes to  ──▶  trace (append-only JSONL, replayable)
```

---

## Why this layer exists

Before it, the repo had **eight** separate things called an orchestrator
(`DynamicOrchestrator`, `MetaOrchestrator`, `SovereignAgentLoop`,
`MultiAgentOrchestrator`, `AmbientSovereignOrchestrator`, `UnifiedAgentFleet`,
`UnifiedMeshPipeline`, `LoopEngine`), no shared tool contract, no shared budget
accounting, and a "sandbox" that graded code with `random.random()`.

This package does not delete those — it gives them one place to converge, and
it is usable on its own from day one.

---

## Setup: start with `doctor`

```bash
cp .env.example .env      # add GROQ_API_KEY=gsk_...
python -m jarvisx.agentic doctor
```

`doctor` checks credentials, backend selection, a **live model round-trip**,
**native tool calling**, and the sandbox — then prints `READY` or `NOT READY`
and exits `1` if you cannot run yet.

```
1. Credentials
  OK GROQ_API_KEY              fingerprint gsk_…79569a95
2. Backend selection
  OK selected backend          openai-compatible:llama-3.3-70b-versatile
3. Live model round-trip
  OK model responded           'PONG' model=llama-3.3-70b-versatile
4. Tool calling
  OK native tool calls         list_files
5. Sandbox
  OK code execution            exit=0 out='42'
  OK path jail                 escape blocked
  OK pytest available          verification checks will run
```

### Why this step exists

This repository has **no `python-dotenv` dependency and nothing loads `.env`
into `os.environ`**. `GroqLLMProvider` works around that with its own ad-hoc
reader (including a hardcoded `E:/project-jarvis-x/.env` path). So a key
sitting in `.env` never reached code reading `os.getenv(...)` — and the agent
silently dropped to the offline heuristic, writing a placeholder file instead
of real code.

`jarvisx.agentic.env.load_dotenv()` fixes that once for the whole layer:
no third-party dependency, walks up to the repo root, and **existing
environment variables always win** so an exported key is never clobbered by a
stale file. `doctor` and every error message run secrets through `redact()`.

### Provider precedence in `AutoBackend()`

`ALFRED_AGENT_BACKEND` → Groq → OpenRouter → OpenAI → local Ollama →
`LLMRouter` → offline heuristic. A `OLLAMA_BASE_URL` ending in `/api`
(what `.env.example` shipped) is normalised to `/v1`, because the OpenAI
shim lives there and the native endpoint would 404.

**The model must support tool calling.** Groq's default here is
`llama-3.3-70b-versatile`. Override with `GROQ_MODEL` or
`ALFRED_AGENT_MODEL`. Without tool support the agent can plan but cannot act.

---

## The five properties that make it a harness

### 1. Provider-agnostic model access

`ModelBackend` is the only seam between the harness and a vendor.

| Backend | Use |
|---|---|
| `ScriptedBackend` | deterministic replay — tests and CI |
| `HeuristicBackend` | offline planner, zero dependencies |
| `OpenAICompatibleBackend` | OpenRouter / Groq / Ollama / vLLM (stdlib `urllib`, no `httpx`) |
| `LLMRouterBackend` | delegates to the existing `jarvisx.llm.LLMRouter` |
| `AutoBackend()` | picks the best available; never raises |

Selection precedence in `AutoBackend`: `ALFRED_AGENT_BACKEND` →
`OPENROUTER_API_KEY` → `GROQ_API_KEY` → `OLLAMA_BASE_URL` → `LLMRouter` →
offline heuristic.

### 2. Tools are contracts, not conventions

Every tool carries a JSON Schema and a permission tier reused from the
existing kernel (`SAFE` / `CONFIRM` / `RESTRICTED` — see
`jarvisx/tools/tool_kernel.py`), so the harness inherits Alfred's security
policy rather than inventing a second one.

Arguments are validated **before** execution. Validation failures, unknown
tools, and policy denials are returned to the model as observations, not
raised — so the model can read the error and self-correct.

```python
from jarvisx.agentic import AgentToolRegistry
from jarvisx.tools.tool_kernel import PermissionLevel

registry = AgentToolRegistry()

@registry.tool(name="deploy", permission=PermissionLevel.CONFIRM)
def deploy(target: str) -> dict:
    """Ship the current build to a target environment."""
    return {"deployed": target}
```

### 3. Execution is genuinely isolated

`SandboxedRunner` runs agent code in a subprocess with:

- a **path jail** — `resolve()` raises `PathEscape` for anything leaving the workspace
- **rlimits** on POSIX: address space, CPU time, file size, process count
- a **timeout** that is actually enforced
- **secret scrubbing** — `*API_KEY*`, `*SECRET*`, `*TOKEN*`, `*PASSWORD*`, cloud prefixes
- `PYTHONDONTWRITEBYTECODE=1`

That last one is not cosmetic. Two submissions whose source files happen to be
the same byte size, written within the same mtime tick, will make CPython
reuse the *previous* `.pyc` — so the harness grades code the agent did not
write. There is a regression test for exactly this
(`test_repeated_evaluation_is_not_fooled_by_stale_bytecode`).

### 4. "Done" is decided by running something

`Verifier` applies checks that execute real code:

| Check | Passes when |
|---|---|
| `python_assert` | the snippet exits 0 |
| `tests_pass` | the sandbox pytest suite exits 0 |
| `file_exists` | the artifact is on disk |
| `output_contains` | every needle appears in output or transcript |
| `nonempty_output` | the answer is non-trivial |
| `json_output` | the answer parses as JSON |
| `CustomCheck` | your predicate says so |

A run that the model *claims* succeeded is downgraded to `FAILED` if
verification does not agree. Checks can be declared as plain data, which is
what lets the planner emit them:

```python
TaskNode(id="implement", instruction="...", verify=[
    {"type": "file_exists", "path": "solver.py"},
    {"type": "tests_pass", "path": "test_solver.py"},
])
```

### 5. Every decision is recorded

`TraceRecorder` appends one JSON line per event to
`var/agentic/runs/<run_id>.jsonl`: `run_start`, `step`, `tool_call`,
`observation`, `loop_guard`, `budget_exceeded`, `run_end`. Replay it with
`jarvisx.agentic trace <file>`. Orchestrations additionally persist
`<graph_id>.orchestration.json`.

---

## Budgets and the loop guard

`Budget(max_steps, max_tool_calls, max_seconds, max_tokens)` is checked at the
top of every iteration. Exceeding any ceiling ends the run as
`BUDGET_EXCEEDED` — which is a *failure* status, never a silent success.

The loop guard fingerprints each `(tool, arguments)` pair; the same call more
than `repeat_limit` times ends the run. This is what stops a stuck model from
burning a budget on one failing action.

Roles carry their own envelopes: `coder` gets 10 steps, `planner` gets 4.

---

## Usage

### One task

```python
from jarvisx.agentic import run_task

result = run_task("List the primes below 100", role="coder")
print(result.status, result.output)
```

### One goal, orchestrated

```python
from jarvisx.agentic import run_goal

report = run_goal("Build a CSV deduplicator with tests")
print(report.ok, report.succeeded, report.failed)
print(report.final_output())
```

### Full control

```python
from jarvisx.agentic import (
    AgentHarness, Budget, Orchestrator, RoleRegistry,
    SandboxedRunner, TaskGraph, TaskNode, Verifier,
)
from jarvisx.agentic.verifier import TestsPassCheck

with SandboxedRunner(workspace="./ws") as sandbox:
    graph = TaskGraph([
        TaskNode(id="build", instruction="write solver.py", role="coder",
                 verify=[{"type": "file_exists", "path": "solver.py"}]),
        TaskNode(id="test", instruction="write and run test_solver.py",
                 role="tester", depends_on=["build"], max_retries=2,
                 verify=[{"type": "tests_pass", "path": "test_solver.py"}]),
    ])
    with Orchestrator(sandbox=sandbox, default_budget=Budget(max_steps=10)) as orch:
        report = orch.run("ship a solver", graph=graph)
```

### CLI

```bash
python -m jarvisx.agentic roles
python -m jarvisx.agentic tools
python -m jarvisx.agentic plan "Build a CSV deduplicator with tests"
python -m jarvisx.agentic run  "Build a CSV deduplicator with tests" --workers 4
python -m jarvisx.agentic task "List the primes below 100" --role coder
python -m jarvisx.agentic runs
python -m jarvisx.agentic trace var/agentic/runs/<run_id>.jsonl
python -m jarvisx.agentic serve --port 8123
```

Add `--backend offline` to force the deterministic planner (no network).

### HTTP control plane

```bash
python -m jarvisx.agentic serve --port 8123
```

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | liveness, backend identity, paths |
| GET | `/tools` | registered harness tools |
| GET | `/roles` | registered agent roles |
| POST | `/plan` | `{goal}` → task graph, no execution |
| POST | `/run` | `{goal, max_steps?}` → full report |
| POST | `/tasks` | `{task, role}` → single harness run |
| GET | `/runs` | recorded runs |
| GET | `/runs/{id}/trace` | replay one run |
| GET | `/events` | SSE stream of live orchestration events |

Built on the standard library's `http.server`, so it needs no extra
dependencies.

---

## Adding a role

```python
from jarvisx.agentic import RoleRegistry, RoleSpec, Budget

roles = RoleRegistry()
roles.register(RoleSpec(
    name="security",
    title="Security Reviewer",
    focus="finding injection, traversal and secret-leakage defects",
    budget=Budget(max_steps=6, max_tool_calls=12, max_seconds=120),
    allowed_tools=("read_file", "list_files", "python_exec", "final_answer"),
    temperature=0.0,
))
```

`allowed_tools` does not hide the other tools — it re-tiers them to
`RESTRICTED`, so the model still *sees* the boundary and gets a clear denial
if it crosses it.

---

## Relationship to the existing subsystems

| Existing | Relationship |
|---|---|
| `jarvisx.tools.tool_kernel` | **reused** — permission tiers, `ToolSpec`, `ToolResult` |
| `jarvisx.llm.llm_router` | **wrapped** by `LLMRouterBackend` |
| `jarvisx.orchestration.sandbox_harness` | **rewired** to `SandboxedRunner`; same public signature, real scoring |
| `jarvisx.orchestration.meta_orchestrator` | predecessor; migrate when ready |
| `jarvisx.agents.sovereign_agent_loop` | predecessor; hardcoded plan templates vs. planned DAG |
| `jarvisx.mesh.*` | orthogonal — distribution. A `ModelBackend` or tool could dispatch to a mesh worker |

---

## Tests

```bash
pytest tests/unit/test_agentic_harness.py \
       tests/unit/test_agentic_orchestration.py \
       tests/unit/test_agentic_control_plane.py \
       tests/unit/test_sandbox_harness_real.py -v
```

Live demonstration:

```bash
python demo_agentic_harness.py            # offline, deterministic
python demo_agentic_harness.py --backend auto   # real model provider
```
