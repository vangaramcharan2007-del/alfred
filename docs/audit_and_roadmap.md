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

**`90deb28` — nine test modules imported their subject by a path that never existed.**
Five files failed at collection because they imported bare names that exist
nowhere in the repository, while the classes under test were in
`jarvisx.integrations` the whole time. One imported `from jarvis.rate_limiter`
— there is no top-level `jarvis` package at all, so it could never have worked
on any machine. Running them for the first time found a real bug:
`TokenBucketRateLimiter.get_status()` returned `self._tokens` without
refilling, and tokens accrue lazily, so a monitoring endpoint reported a bucket
as permanently empty. Three more assertions compared a float token count to
exact equality when the bucket legitimately accrues microtokens between the
action and the assert.

**`2ad2424` — a sandbox escape in the code that executes LLM-written code.**
`DynamicToolForge`'s safety gate was a regex blocklist over raw source text. A
text scan cannot see `().__class__.__bases__[0].__subclasses__()`, because that
contains none of the blocked words; it reaches every class in the process,
including `subprocess.Popen`. Replaced with an AST-based validator that rejects
blocked builtins, blocked module imports, and any attribute in the dunder
escape set — which also removes the regex's false positives, so a function
legitimately named `execute_query` no longer trips `\bexec\b`.

**`44de795` — the swarm's model was hardcoded and its "parallelism" used one OS thread per agent.**
`SwarmOrchestrator.__init__` took no arguments and hardcoded
`self.model = "qwen2.5-coder:1.5b"`. `_run_agent` wrapped a blocking
`ollama.chat` in `asyncio.to_thread`, so every sub-agent held a real thread for
its whole lifetime and fan-out was bounded by the thread pool rather than by
`max_agents`. It now holds one `ollama.AsyncClient()` and awaits it.

**`ca87577` — two filesystem guards that did not guard anything.**
`_is_system_path()` held only Windows prefixes and compared against
`Path(p).resolve()`. On POSIX a backslash is an ordinary filename character, so
`C:\Windows\system32\malware.exe` resolved to
`/home/user/alfred/C:\Windows\system32\malware.exe`, matched nothing, and the
write succeeded — a tracked 3-byte file with that literal name, containing
`bad`, was sitting in the repository root, left behind by the security test
that was supposed to prove the write could not happen. Separately,
`ReadFileTool.execute()` had **no path check at all**: `read_file("../../../etc/passwd")`
returned `status="success"` with the contents, and so would `~/.ssh/id_rsa`.

**`7ebd357` — three test files removed.** Two tested `EVMasterAutomationEngine`
and `EVOmniScreenSentinel`, classes that do not exist; `git log --all` on the
module paths returns empty, so the production modules were never committed and
the nine test methods had no passing state to return to. The third,
`tests/test_live_anti_hallucination.py`, was not a test file: zero `def test_`
functions, 36 top-level calls that ran the moment pytest imported it, including
live LLM prompts, launching the Windows `notepad` binary, writing files into
the repo, and a 15-second polling loop. It closed by printing
`ALL 6 LIVE VERIFICATION TESTS PASSED WITH 100% REAL EXECUTION`.

### Still open: 13 imports of two modules that were never written

`ev_master_automation_engine.py` and `ev_omni_screen_sentinel.py` do not exist
and never did, but 13 import sites across six production files still reference
them:

```
src/jarvisx/automation/ev_autonomous_daemon.py     (4 sites)
src/jarvisx/voice/ambient_dual_sentinel.py         (3)
src/jarvisx/tools/builtin_tools.py                 (2)
src/jarvisx/voice/ev_handy_engine.py               (1)
src/jarvisx/voice/voice_pipeline_e2e.py            (1)
src/jarvisx/gui/ev_minimalist_logo_overlay.py      (1, module level)
```

Twelve are inside function bodies, so the failure is deferred to call time
rather than caught at import — which is exactly why an import-time audit does
not see them. The features they back (F9 screen-math vision, F10 thermal/RAM
purge, WhatsApp send, the omni screen sentinel) cannot run on any machine.
Removing the call sites is not an audit cleanup but a product decision, so it
is recorded here rather than done.

### Resolved: five capabilities that were built but not reachable by voice

A different category from the above, and easy to confuse with it. These
subsystems **existed and worked**; what was missing was the routing from
`DynamicOrchestrator._execute_single_voice_command`, which fell through to
`action: "speak"` instead of dispatching to them.

| Capability | Exists at | Action now returned |
|---|---|---|
| Chess | `games/chess_engine.py` (`ChessGame`) | `chess_start`, `chess_move` |
| DSA tutor | `tutor/dsa_tutor.py`, wired in `interface/cli.py:770` | `dsa_tutor` |
| VS Code control | `automation/vscode_controller.py` | `vscode_control`, `vscode_type` |
| Multi-step missions | `missions/unified_mission_planner.py`, wired to `DynamicOrchestrator.execute_mission()` at line 448 | `mission` |
| Temp-storage cleanup | `automation/real_system_cleaner.py`, assigned to `self.cleaner` at line 44 and never called | `clean` |

All six routes were added to `_execute_single_voice_command` in commits
`3c235cb`, `16421f7` and `a578eba`, and verified by driving the real
`DynamicOrchestrator`:

```
$ play chess with me      -> chess_start    SUCCESS  "Visual Chess Arena opened in browser." + board
$ move e4                 -> chess_move     SUCCESS  "You played e2->e4. Alfred played b8->c6."
$ teach me dsa            -> dsa_tutor      SUCCESS  "Welcome to Day 1 ... Arrays & Hash Maps ..."
$ control vs code         -> vscode_control SUCCESS  "VS Code is under control -- focused and ready."
$ do it yourself in vs code -> vscode_type  SUCCESS  "created 'array_implementation.py' and loaded it"
$ mission give me a system overview -> mission completed  steps=1 completed=1 tool=get_system_info
```

The chess game is held on `self._chess_game` so that a bare `"move e4"` refers
to the game the previous command started, rather than inventing a fresh board.
The mission route passes `interactive=False`, because a hands-free agent must
not block on stdin waiting for a prompt the user cannot see.

The mission route is worth pausing on. `execute_mission()` had been wired to
`UnifiedMissionPlanner` since it was written — the gap was purely that nothing
in the voice path called it. Its `status: "completed"` was checked rather than
trusted, since a planner that reports completion with nothing executed is the
same false-success bug found in `execute_swarm`; here it is backed by a real
`get_system_info` call with `completed_count` matching `steps_count`.

One correction to the earlier reasoning recorded here: this was described as
belonging to Phase 2, on the grounds that the routes should be added once the
12 orchestrators are collapsed into one. That was wrong — the engines import
cleanly and were testable immediately, so there was no dependency on the
consolidation. Wiring them first also gives Phase 2 five concrete routes that
the single surviving orchestrator must keep answering, which is a useful
acceptance test for the merge rather than an argument for waiting.

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
| Agentic suite | **553 passed**, 0 failures |
| Full suite | **7 failed / 1097 passed / 5 skipped / 3 errors** |
| Baseline before this work | 38 failed / 751 passed / 56 errors |

Identical across two consecutive runs. Progression through the audit:
751 → 781 → 862 → 1000 → 1014 → 1017 → 1045 → 1051 → 1060 → 1065 → 1076 →
1086 → 1088 → 1089 → 1090 → 1091 → 1092 → 1093 → 1094 → **1097** passing,
with collection errors 56 → 3 and failures 38 → 7. Most of the gain in passing
tests came from installing the declared dependency set, which let whole files
collect for the first time; the drop in failures came from fixing what those
newly-running tests found.

The steps after 1076 are the work described above: chess took the suite to
1086, the DSA tutor plus VS Code routes to 1088, the `_execute_subsystem` fix
to 1089, the mission route to 1090, removing an order dependency from the
sentinel test to 1091, correcting the crest labels to 1092, threading router
injection through the organism to 1093, and the temp-cleanup route to 1094.

### Three silent-failure fixes found while chasing the remaining failures

**`_execute_subsystem` accepted a `category` and never used it.** It returned
whatever the ReAct turn produced, so a caller had no way to tell which
subsystem had been asked to handle a request. `test_dynamic_orchestrator_
subsystem_dispatch` died on `KeyError: 'subsystem'`. The category is now
recorded on the result, and the docstring no longer claims "Pure Autonomous
LLM Multi-Agent Reasoning Engine" with "multi-step directives through genuine
LLM reasoning" — every category routes to the same single ReAct turn.

**`execute_swarm` reported success when every agent timed out.** Its status was
a hardcoded `"success"`. Reproduced directly: with `timeout_per_agent=0.05` and
every agent sleeping 1.0 s, it returned `agents_succeeded=0`,
`merged_response=''` and `status='success'`. Status is now derived —
`COMPLETED` / `PARTIAL` / `FAILED` — and the timeout and error counts are
surfaced so the caller need not recount `individual_results`.

**A test that passed alone and failed in the suite.**
`test_organism_fastpath_integration` was 7/7 green when its file ran by itself
and failed in the full suite with `RuntimeError: There is no current event loop
in thread 'MainThread'`. It called `asyncio.get_event_loop()` and then
`run_until_complete`, which only works while nothing earlier in the same
process has unset the current loop — `get_event_loop()` has not created a loop
on demand since Python 3.10. The test was asserting something about test
ordering, not about the organism. `asyncio.run()` gives it its own loop either
way. Worth naming because a failure that depends on what ran before it will
move around and look like a different bug each time.

### The one that mattered: an injected model could not reach the brain

`Brain._get_router()` lazily constructed its own `LLMRouter()` and nothing could
supply one. `AlfredOrganism` took only a persona and `get_organism()` took
nothing, so `think()` and `decide_action()` — every model call the organism
makes — went to a router no caller could configure.

This is why fixing the orchestrator's ReAct turn changed nothing on its own:
`_execute_single_voice_command` step 1 routes through
`get_organism().react_turn()`, not through `execute_llm_react_turn_async()`. The
same discarded-dependency bug existed one level up, on the path actually taken.

An optional `router` now threads through `Brain` → `AlfredOrganism` →
`get_organism`, and the orchestrator passes `self.llm_router` at both step-1
call sites. `get_organism()` applies the router to the singleton even when that
singleton already exists; without that override the first caller to touch the
organism would permanently pin the default router and every later injection
would be ignored — the same bug relocated rather than removed. The other 16
`get_organism()` call sites omit the parameter and are unchanged.

Verified end to end through `execute_voice_command()` with a probe router:

```
probe calls : 1
response    : 'INJECTED-ROUTER-REACHED-THE-BRAIN'
```

**This is the prerequisite for the Phase 2 consolidation**, not a substitute for
it. The 12 orchestrators still exist; what changed is that a model can now
actually be handed to the one that runs.

### A wrong diagnosis, corrected: why `test_router_both_providers_failure` fails

Recorded here because the first two explanations given for this one were both
false, and the correct answer is a useful warning about reading selection code.

The test registers two failing providers and asserts `primary == "ollama.local"`.
It gets `gemini.google`. Two plausible-sounding explanations were checked and
refuted:

- *"Auto-registration clobbers same-named providers."* False.
  `_ensure_default_providers()` guards every registration with
  `if not self.registry.get(name)`. Verified: a stub registered as
  `ollama.local` survives router construction intact.
- *"Gemini reads as available in the registry, so the router falls through to
  it."* False, and the reason a stub registered as `gemini.google` did not fix
  the test.

The actual cause: `select_model()` never reads the registry at all. It scores
`self.profiles` — a static list — and returns the highest. Measured in this
environment: `gemini.google` at score 0.892, with profile order
`ollama.local ×4, gemini.google ×2, openrouter.gateway, omniroute.gateway ×2`.
Provider health and registry contents are irrelevant to the choice.

So the test asserts a score-dependent outcome as though it were fixed. It passes
only where local Ollama outscores the cloud profiles. That makes it
environment-dependent, in the same bucket as the hardware and network failures
— not a production bug, and not fixable from the registry side.

### Resolved: three swarm tests that had never tested anything

Both of their mock branches were dead:

| The test matched on | What the source actually does |
|---|---|
| `"Decompose this intent" in user_msg` | `decompose()` sends `"Break this complex request into 2-N independent sub-tasks…"` (line 65) |
| `"Lead Swarm Synthesizer" in system_msg` | the module never sends a system message at all — only a single user message |

Every mocked call therefore fell through to its default branch. Those three
tests never once exercised the fan-out, the timeout path or the status
derivation they were written for. They also asserted a result schema
(`subtasks_count`, `unified_response`, `swarms_executed`) that this module has
never had; the real keys are `agents_deployed`, `agents_succeeded`,
`agents_timed_out`, `agents_failed`, `individual_results` and
`merged_response`.

Rewritten against the real prompt and the real schema in `bd57a43`. The timeout
test now genuinely times an agent out and asserts `PARTIAL` — which means it
would now catch the hardcoded `"success"` status fixed in `952763d`. Before, it
could not have, because it never reached the timeout path.

The decompose fallback test now asserts the actual graceful contract: one
runnable task with `task_id`/`description`/`prompt`. It previously demanded two
sub-tasks and a `role` key. Fabricating a split from an intent the LLM failed to
parse would mean sending the same prompt to two agents and calling that
parallelism, and `role` appears nowhere in the prompt `decompose()` sends.

`SwarmOrchestrator` still has **zero callers** outside its own module. The
synthesis step the old tests imagined was never built, and building it remains
a Phase 2 decision rather than something to add to dead code — but the tests no
longer pretend it exists.

**Those numbers were not reproducible when first written, and that is its own
finding.** Re-running the full suite twice back to back, same environment, same
collection order, gave 31 failed / 1062 passed and then 28 failed / 1065
passed. Three release tests failed only on some runs:

```
test_phase87_sovereign_release.py::test_sovereign_release_manager_manifest_generation
test_phase87_sovereign_release.py::test_kernel_objective_routing_phase87
test_phase90_grand_finale.py::test_grand_finale_release_manifest_generation
```

All three asserted `total_hspw_achieved >= 40.0`. That figure is the sum of
~24 per-subsystem counters read off `PersonalOSKernel` (`personal_os.py:635`),
each of which accumulates mutable state at runtime. In a clean process the
total is a deterministic **45.5** and they pass; inside a full-suite run
something earlier has already moved those counters and the total lands at
**39.5**, half a unit under the threshold. So the assertion was not measuring
the release engine at all — it was measuring whatever had run before it.

Fixed in `fc7cdb7` by asserting the contract each engine actually implements
(the milestone flag must agree with the value it was derived from) rather than
an absolute threshold on a contaminated aggregate. Verified across three
consecutive full-suite runs — warm `var/` twice, and once with `var/` moved
aside, the cold condition that had produced 31. All three agree on
28 / 1065 / 5 / 4.

A suite that cannot reproduce its own result cannot be used to judge anything,
so this mattered more than the three tests it unblocked. It is also a warning
about the numbers elsewhere in this document: **any count quoted here should be
treated as suspect until it survives a second run.**

**A correction to something this document claimed earlier.** An earlier
revision of this section said the failures and collection errors "are all
`ModuleNotFoundError` for optional dependencies this sandbox does not have",
and that installing them was a five-minute job. That was wrong, and it was
wrong in the direction that matters.

The claim was made *before* installing the declared dependency set. Installing
it did not clear the failures — it exposed what they had been hiding. A
collection error stops a whole file from running, so 56 errors were masking
several hundred tests that had never executed. Once the declared deps were
installed, those tests ran, and a substantial share of them failed for reasons
that had nothing to do with a missing package:

- `LLMRouterBackend.complete()` returned `""` wrapped in `finish_reason="stop"`,
  so the harness recorded empty runs as `SUCCEEDED`.
- `AutoBackend()` treated successful router construction as capability and
  selected an unservable backend ahead of the offline heuristic.
- `DynamicToolForge`'s regex safety gate let the interpreter escape
  `().__class__.__bases__[0].__subclasses__()` through to `Popen`.
- `_is_system_path()` was a no-op on every platform except Windows, and
  `ReadFileTool` had no path guard at all.
- `TokenBucketRateLimiter.get_status()` reported a token count that could only
  ever go down.
- Nine test modules imported their subject by a path that had never existed.

The lesson is the one worth keeping: **a failing test can hide the real failure
count, and so can a missing dependency.** Install the declared dependency set
before drawing any conclusion about a repository's health — in either
direction. Note also that installing dependencies *raised* the visible failure
count (38 → 50) as masked tests began to run. That was progress, not
regression, and a dashboard that only reports a green/red count would have read
it as the latter.

The 3 remaining collection errors are genuinely environmental and were checked
individually: `test_ambient_dual_sentinel.py` and `test_ev_handy_engine.py`
need the PortAudio system library (`OSError: PortAudio library not found`, not
a Python package, and not pip-installable — the `pyaudio` wheel fails to build
here because there is no `libportaudio` and no `portaudio.h`);
`test_ev_minimalist_logo_overlay.py` needs `tkinter`, which ships with the
system Python rather than pip.

An earlier revision of this paragraph claimed a fourth error in
`test_ev_max_agent.py` caused by `pygame` being "imported but not declared in
`pyproject.toml`". Both halves were wrong and have been corrected: `pygame` is
declared at `pyproject.toml:47`, and `test_ev_max_agent.py` exists and
collects without error.

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
  candidate: it has budgets, a policy gate, tracing, verification and 553
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
Three shipped modules were unreferenced by the agent:
`sovereign_wake_word_engine.py` (now partially wired via `WakeWordInput`),
`ambient_dual_sentinel.py`, and `full_duplex_controller.py`.

`full_duplex_controller.py` is now wired (commit `6a41516`). `InterruptibleOutput`
in `agentic/voice_loop.py` wraps any `SpeechOutput` with a
`FullDuplexVoiceController`, splits a reply into sentences, and listens for a
barge-in between them. Measured: a three-sentence reply interrupted after the
first delivers exactly one spoken sentence and leaves the controller in
`DuplexState.INTERRUPTED`; `trigger_barge_in()` returns to `LISTENING` in
0.01 ms with an audit hash recorded. So the interruption gap described in the
earlier revision of this document is closed, and the assistant can be talked
over rather than waited for.

What is still open here is `ambient_dual_sentinel.py`, which cannot even be
imported in this sandbox (`OSError: PortAudio library not found`). Wiring it
blind would ship code nobody has run, which is the failure mode this audit
exists to catch, so it is left for the real machine.


---

## 4. The honest summary

The architecture was never the problem. There is a working agentic harness with
budgets, a policy gate, verification and tracing, and 553 tests pass against it.

The problems are **duplication** (twelve orchestrators), **unverified claims**
(136 self-graded, 84 simulated), and **unwired real code** (189 unreachable
files that mostly work). None of those are fixed by deleting files, which is why
I deleted four and stopped.

And the one thing that matters most cannot be done in this sandbox: nobody has
yet run this against a real model on a real machine with a real microphone.
That is Phase 1, and it should happen before anything else on this list.
