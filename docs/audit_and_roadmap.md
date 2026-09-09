# Alfred: Audit and Roadmap

Measured on branch `arena/01a0826c-alfred` at `f23d6f5`.

Every number here came from a script run against the working tree, not from
reading files by eye. The scripts are described inline so any claim can be
re-checked.

---

## 1. What I found

### The repo is not full of junk. It is full of unwired code.

I went in expecting to delete a lot. I could not justify it, and the reason
matters more than the count.

| Measurement | Value |
|---|---|
| Python files | 1110 |
| Lines | ~144,000 |
| Subpackages under `src/jarvisx/` | 78 |
| Modules that import cleanly | 439 |
| Modules that fail to import | 58 |
| …of those, failing on a **missing pip package** | 58 |
| …of those, failing on a **code fault** | **0** |
| Files reachable from the declared entry points | 499 |
| Files reachable from the test suite | 474 |
| Files neither entry point nor test can reach | 189 |
| Files referenced by **nothing at all** | 22 |

That last row is the important one. My first pass reported 115 dead files. It
was wrong, and worth being precise about why: it treated "no other file imports
this" as "nothing uses this", which silently flagged `jarvisx/cli.py` and
`jarvisx/__main__.py` — the two console-script entry points declared in
`pyproject.toml`. Packaging config references them; no `import` statement ever
will. A deletion list built on that heuristic would have removed the CLI.

Re-run with entry points, `pyproject.toml`, docs, scripts and the demo all
counted as references, the honest number is **22 files, 1558 lines**.

Then I read them. `voice/eevee_live.py` is a 310-line Gemini Live duplex voice
implementation using `pyaudio` and `google.genai`. It is unreferenced, but it
is not dead — it is a real feature nobody wired up, and it is the Eevee voice
this project was asked for. `automation/ghost_browser.py`,
`security/swarm_blockchain.py`, `memory/rem_sleep.py` and the rest are the same
shape: plausible, implemented, unreachable.

**So I deleted four files and stopped.** Deleting 1500 lines of real
implementation because a reachability script could not see a caller would
destroy work, not remove junk. The right fix for unwired code is to wire it or
to decide deliberately that it is abandoned — not to let a heuristic decide.

### Duplication is the actual problem

The same job is implemented several times, and most copies are live:

| Module name | Copies | Status |
|---|---|---|
| `event_bus.py` | 3 | all three reachable |
| `mission_executor.py` | 3 | all three reachable |
| `registry.py` | 3 | all three reachable |
| `capability_registry.py` | 4 | 3 reachable, 1 orphan |
| `research_agent.py` | 2 | both reachable |
| `planner.py` | 2 | both reachable |
| `*Orchestrator` classes | 12 | 8 prod, 2 test, 2 orphan |

Twelve orchestrators is not twelve features. It is one feature discovered
twelve times, and every copy is a place a bug can hide that the others do not
have.

---

## 2. What I fixed

Five commits, all verified, all pushed.

**`5219109` — one missing import was killing seven modules.**
`tools/operational_db.py` annotated a parameter `Optional[SupabaseClient]`. No
`SupabaseClient` exists anywhere in the repository. Annotations evaluate at
class-definition time, so the module raised `NameError` on import — and because
seven modules import it transitively, seven modules were dead:

```
jarvisx.tools.operational_db      jarvisx.core.configuration
jarvisx.core.proactive_monitor    jarvisx.core.world_model
jarvisx.tools.computer_control    jarvisx.tools.personalization
jarvisx.tools.xp
```

The client is now duck-typed and optional. Verified both ways: constructed with
no client (sync off, `set`/`get` round trip, `sync_unsynced` a no-op, `close`
joins the worker thread), and with an injected client (sync on, the record
actually reaches `insert`). Importable modules 432 → 439.

**`f23d6f5` — four dependencies were imported but never declared.**
A fresh `pip install -e .` produced a broken install:

- `numpy` — 6 modules import it. It was arriving transitively via
  scipy/pandas/scikit-learn, so any resolver change could have removed it.
- `watchdog` — 2 modules.
- `edge-tts` — 4 modules doing neural TTS; added to the `[voice]` extra.
- `pywin32` — 3 modules use `win32gui`; added to `[desktop]` **with a
  `sys_platform == 'win32'` marker**, because declaring it unmarked breaks
  every Linux and macOS install.

Every third-party import in `src/` is now declared.

**`60b7025` + `b39c538` — pyflakes found 45 undefined names; four were live
runtime bugs.**

I ran pyflakes over `src/` looking for more faults of the SupabaseClient shape.
It reported 45 undefined names. Thirty-five were missing `typing`/stdlib imports
(`Optional`, `Any`, `Dict`, `Tuple`, `Path`, `re`) across 16 modules. Those
differ from the SupabaseClient bug only in that the annotation is not evaluated
at import time — so the module loads, and then raises `NameError` the first time
the function is called.

The remaining ten needed reading. Four were genuine runtime bugs:

- `integrations/llm_prompt_lru_cache.py` defined `HashableKey` at the bottom of
  the file and used it in four annotations above. Importing raised `NameError`,
  so **the entire prompt cache was unusable.** Verified working after the fix:
  put/get, TTL expiry, LRU eviction, and the decorator (a second identical call
  is served from cache; the underlying function runs once).
- `interface/cli.py` `_handle_mission(self, args)` read `command` and
  `raw_input`, neither of which is a parameter of that method — `raw_input`
  belongs to `handle_command_async`. So `models`/`llm`/`gateways` never routed,
  and **every fall-through to the orchestrator raised `NameError` instead of
  running the command.** The identical expression at line 1119 sits inside
  `handle_command_async`, where `raw_input` *is* in scope, and was left alone.
- `gaming/game_optimizer_agent.py` called `os_optimizations.append(...)` inside
  a `try`, but created the list six lines later. The `NameError` was swallowed
  by `except Exception` and logged as a *"Visual actuator note"* — **hiding the
  real fault and silently losing the entry.**
- `automation/dynamic_orchestrator.py` logged to a module-level `logger` that
  did not exist from two call sites. Any exception there would have raised
  `NameError` *while handling the original error*, destroying the diagnosis.

The other six were unresolvable forward-reference annotations: `ReviewReport` →
the already-imported `AdversarialReviewReport` (which is what
`review_code_or_diff` actually returns), and `JarvisRuntime` / `ToolRegistry`,
both real classes that were simply never imported, now brought in under
`TYPE_CHECKING`.

**Undefined names in `src/`: 45 → 0.**

pyflakes also reports 1005 unused imports, 146 f-strings with no placeholders
and 86 assigned-but-unused locals. Those are noise, not faults, and were left
alone deliberately.

**`5474b26`, `bde6b6a`, `74ba775` — four provably dead files removed.**

- `tools/workflow.py` imported `WorkflowEngine` from `jarvisx.core.workflows`.
  Neither exists. Nothing imported the file. Unfixable without writing an
  engine no caller needs.
- `src/program1_1d_array.py`, `src/program2_2d_array.py` — 11- and 16-line
  numpy array-indexing exercises at the `src/` root.
- `src/jarvisx/games/print(sum of two num).py` — 42 bytes,
  `print(sum of two num)`, did not parse. The only syntax error in 1114 files.

### Verification

| Check | Result |
|---|---|
| Agentic suite | **544 passed**, 0 failures |
| Full suite | 38 failed / 781 passed / 56 errors |
| Baseline before this work | 38 failed / 751 passed / 56 errors |

The 38 failures and 56 errors are unchanged and pre-existing. They are all
`ModuleNotFoundError` for optional dependencies this sandbox does not have
(`psutil`, `PIL`, `yaml`, `fastapi`, …). Six packages account for 77% of them;
installing them is a five-minute job on a real machine.

---

## 3. Next phases

Ordered by what unblocks the most for the least risk. Each is independently
shippable.

### Phase 1 — Make the real machine provably work
**The highest-value work, and the only work that cannot be done here.**

This sandbox has no microphone, no desktop, no browser and no network egress to
model APIs. So the following are unit-tested but never executed for real:
the live Groq model path, wake-word audio, TTS, the active-window sensor, and
`--physical` actually opening an app.

1. On your machine: `pip install -e ".[voice,vision,desktop,dev]"`.
2. `python -m jarvisx.agentic doctor` — it probes ears, mouth, eyes, hands,
   preferences and personas, and tells you which are live.
3. Put your Groq key in `.env`, re-run `doctor`, confirm it stops saying
   *"no model key — agent work will write a placeholder, not real code"*.
4. `python -m jarvisx.agentic alfred --persona eevee --physical`.

Expected: `doctor` goes green on ears/mouth/hands, and the agent runs on a real
model instead of the heuristic. **Anything that fails here is a real bug I
cannot see, and it should be fixed before any new feature is built.**

### Phase 2 — Collapse the duplicates
Pick one canonical implementation per concept and delete the rest:

- 12 orchestrators → 1. `agentic/scheduler.py::Orchestrator` is the strongest
  candidate: it has budgets, a policy gate, tracing, verification and 544
  passing tests behind it.
- 3 event buses → 1. 3 mission executors → 1. 4 capability registries → 1.

Do this behind the test suite, one concept at a time, and expect the file count
to drop by hundreds. This is the single biggest reduction in "where could this
bug be hiding".

### Phase 3 — Decide the fate of the 22 unwired files
Not deletion by heuristic. For each: **wire it, or delete it on purpose.**
The obvious first candidate is `voice/eevee_live.py` — a real Gemini Live
duplex voice implementation that nothing calls, for the exact voice this
project was asked for. Wiring it is a feature; deleting it is a decision. Both
are better than leaving it.

### Phase 4 — Replace the self-graded claims with evidence
136 places in `src/` assert their own completeness (`100%`, `COMPLETE`,
`production ready`), and 84 files carry `simulate`/`mock`/`fake`/`placeholder`
markers. None of that is checked by anything. The pattern already exists in
`agentic/`: `doctor` probes a capability and reports `OK` or `--` based on
actually calling it. Extending that discipline is what turns a claim into a
fact.

### Phase 5 — Wire the ambient layer
Three shipped modules are still unreferenced by the agent:
`sovereign_wake_word_engine.py` (now partially wired via `WakeWordInput`),
`ambient_dual_sentinel.py`, and `full_duplex_controller.py`. The last is what
makes interruption work — being able to talk over the assistant instead of
waiting for it to finish. That is the remaining gap between this and the
demos you are comparing against.

---

## 4. The honest summary

The architecture was never the problem. There is a working agentic harness with
budgets, a policy gate, verification and tracing, and 544 tests pass against it.

The problems are **duplication** (twelve orchestrators), **unverified claims**
(136 self-graded, 84 simulated), and **unwired real code** (189 unreachable
files that mostly work). None of those are fixed by deleting files, which is why
I deleted four and stopped.

And the one thing that matters most cannot be done in this sandbox: nobody has
yet run this against a real model on a real machine with a real microphone.
That is Phase 1, and it should happen before anything else on this list.
