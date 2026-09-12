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
| Subpackages under `src/jarvisx/` (dirs with `__init__.py`) | 52 |
| Modules on disk under `src/` | 749 |
| Modules that import cleanly | 716 |
| Modules that fail to import | 33 |
| …of those, failing on a **missing dependency** | 33 |
| …of those, failing on a **code fault** | **0** (see caveat) |
| Files reachable from the declared entry points | 550 |
| Files reachable from the test suite | 536 |
| Files neither entry point nor test can reach | 180 |
| Files referenced by **nothing at all** | ~~22~~ **95** — see Phase 3 caveat |

**Caveat on the reachability rows.** Measured by resolving the three console
scripts in `pyproject.toml` (`jarvisx.cli:main`, `jarvisx.__main__:main`,
`friday.__main__:main`) plus `jarvisx.main`, `jarvisx.agentic.__main__` and
`main`, then following static imports transitively: **550** files reachable from
entry points, **536** from the test suite, **569** from either, and **180** from
neither, out of 749. The doc previously said 499 / 474 / 189. The headline
"neither" figure was close; the two components were each off by 50-60, so
whichever traversal produced them did not match the one described here.

Those 180 are an **upper bound on dead code, not a list of it.** The traversal
follows static imports only, and seven sites in this codebase load modules by
computed name or file path — see the Phase 3 caveat. Any file reachable only
through the skills loader, the tool forge or the plugin fleet lands on this list
while being perfectly live at runtime.

**Caveat on the zero.** It is correct, and it is also luck. Importing each of
the 749 modules in `src/` produces 716 clean imports and 33 failures, every one
of them a missing dependency — `pyperclip` ×5, `pystray` ×2, PortAudio ×2, and
one each of `playwright`, `pynput`, `pyautogui`, `pygetwindow`, `tkinter`,
`winreg`, `twilio` and `win32gui`. None is a fault in this codebase.

But one of those 33 is hiding a real fault. `gui/ev_minimalist_logo_overlay.py`
fails at line 16 with `ModuleNotFoundError: No module named 'tkinter'`. At line
25 it does:

    from jarvisx.automation.ev_master_automation_engine import EVMasterAutomationEngine

and no such module exists anywhere in the tree. On a machine that *has* tkinter,
that import fails — on every platform, unconditionally. It is recorded as a
missing-dependency failure here only because tkinter dies first and Python never
reaches it. So "zero code faults" is the right count and the wrong impression:
the audit cannot see a code fault that an absent dependency is standing in front
of, and there is at least one.

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
| `*Orchestrator` classes | 11 | 8 referenced, 3 orphan |

Eleven orchestrators is not eleven features. It is one feature discovered
eleven times, and every copy is a place a bug can hide that the others do not
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

### Still open: 18 imports of six modules that were never written

**This section originally said 13 imports of two modules. The two-module part
was right and the scope was not.** Re-measured by parsing every file in `src/`
with `ast` and resolving each first-party import against the set of modules that
actually exist on disk, the true figure is **18 import statements across 10
files, referencing 6 modules that were never written**.

The two this section already named account for 13 of those sites in 6 files,
exactly as recorded. The other four modules, and the five sites that reference
them, were missing from the audit entirely:

```
automation/task_scheduler.py:143      -> automation.smart_notifier
kernel/jarvisd.py:206                 -> browser.ghost_browser
main.py:92                            -> automation.glowing_waveform_overlay
main.py:155                           -> automation.glowing_waveform_overlay
organism.py:292                       -> vision.ocr_engine
```

Two of those matter more than the `ev_*` ones. `organism.py` is the file that
builds the `Brain`, so a reference to `vision.ocr_engine` sits on the main
reasoning path rather than in a peripheral GUI tool. `main.py` is a declared
entry point, and it references `glowing_waveform_overlay` twice.

Full distribution of all 18 sites:

```
automation.ev_master_automation_engine    10 sites
automation.ev_omni_screen_sentinel         3
automation.glowing_waveform_overlay        2
automation.smart_notifier                  1
browser.ghost_browser                      1
vision.ocr_engine                          1
```

The two modules below account for 13 sites across these six files:

```
src/jarvisx/automation/ev_autonomous_daemon.py     (4 sites)
src/jarvisx/voice/ambient_dual_sentinel.py         (3)
src/jarvisx/tools/builtin_tools.py                 (2)
src/jarvisx/voice/ev_handy_engine.py               (1)
src/jarvisx/voice/voice_pipeline_e2e.py            (1)
src/jarvisx/gui/ev_minimalist_logo_overlay.py      (1, module level)
```

Most sit inside function bodies, so the failure is deferred to call time rather
than caught at import — which is exactly why an import-time audit does not see
them, and why the count here had to be measured by parsing the source rather
than by importing it. The features they back (F9 screen-math vision, F10 thermal/RAM
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
11 orchestrators are collapsed into one. That was wrong — the engines import
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
| Agentic suite | **584 passed**, 0 failures |
| Full suite | **2 failed / 1131 passed / 7 skipped / 3 errors** |
| Baseline before this work | 38 failed / 751 passed / 56 errors |

Identical across two consecutive runs. Progression through the audit:
751 → 781 → 862 → 1000 → 1014 → 1017 → 1045 → 1051 → 1060 → 1065 → 1076 →
1086 → 1088 → 1089 → 1090 → 1091 → 1092 → 1093 → 1094 → 1097 → 1098 →
**1131** passing, with collection errors 56 → 3 and failures 38 → 2. Most of the gain in passing
tests came from installing the declared dependency set, which let whole files
collect for the first time; the drop in failures came from fixing what those
newly-running tests found.

The steps after 1076 are the work described above: chess took the suite to
1086, the DSA tutor plus VS Code routes to 1088, the `_execute_subsystem` fix
to 1089, the mission route to 1090, removing an order dependency from the
sentinel test to 1091, correcting the crest labels to 1092, threading router
injection through the organism to 1093, and the temp-cleanup route to 1094.

After that: the clarification gate and its 31 tests took the suite to 1130,
fixing the misreported `primary` in the router to 1131. Failures fell 5 → 2, the
remaining two both requiring resources this sandbox does not have. Skips rose
5 → 7 when the two browser tests started skipping on a missing dependency
instead of failing on it.

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
it. The 11 orchestrators still exist; what changed is that a model can now
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

**This was itself a wrong diagnosis, and the third one.** It concluded the test
was environment-dependent and the product was fine. It was not.

`select_model()` scoring a static list is real but is not the defect. The defect
is one line in `route_request()`:

    provider = self.registry.get("ollama.local") or self.registry.get(profile.provider_id)

The primary attempt always resolves to `ollama.local` when it is registered —
which `_ensure_default_providers()` makes the normal case. Every `success`
return correctly reported `ollama.local`. But all three `provider_unavailable`
returns reported `profile.provider_id` instead: the highest-*scoring* profile,
which is a different provider from the one that was actually called. The
returned error text contradicted its own field — "Both local Ollama and cloud
OpenRouter failed" beside `primary: gemini.google`.

That is a production bug of the same shape as the hardcoded `"status": "success"`
in `execute_swarm`: a status field that does not describe what happened. It was
fixed by resolving the id once and reporting that, in all three places, leaving
resolution order unchanged. `test_openrouter_fallback.py` is now 7 passed.

The lesson is worth keeping: two refuted explanations made a third, plausible
one look settled. "I have eliminated the wrong answers" is not the same as "I
have found the right one", and the test in question was never environment-
dependent at all.

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

The 3 remaining collection errors were checked individually. Two are genuinely
environmental: `test_ambient_dual_sentinel.py` and `test_ev_handy_engine.py`
need the PortAudio system library (`OSError: PortAudio library not found`, not
a Python package, and not pip-installable — the `pyaudio` wheel fails to build
here because there is no `libportaudio` and no `portaudio.h`).

The third is only partly environmental, and an earlier revision of this
paragraph said it was `tkinter` and stopped there. That is what fails *here*,
but it is not the only thing wrong. `ev_minimalist_logo_overlay.py` line 25
also imports `jarvisx.automation.ev_master_automation_engine` at module level,
and that module does not exist anywhere in `src/`. So on a machine that *does*
have `tkinter` — which is most of them, since it ships with the system Python
rather than pip — the import simply fails one line later instead. The file
cannot be imported on any platform.

Nothing in `src/` imports it; its only importer is its own test. So it is both
dead and broken, which makes it a Phase 3 decision rather than a fix: writing
the missing engine would be inventing a feature, and deleting the file is
destructive and needs a decision rather than a heuristic.

An earlier revision of this paragraph claimed a fourth error in
`test_ev_max_agent.py` caused by `pygame` being "imported but not declared in
`pyproject.toml`". Both halves were wrong and have been corrected: `pygame` is
declared at `pyproject.toml:47`, and `test_ev_max_agent.py` exists and
collects without error.

---

### A bug class worth naming: Windows-only calls on a Linux target

This project's own HUD is titled `SPIDER-MAN EV // DUAL-CORE LINUX
WORKSTATION` and reports `WSL2 LINUX ENGINE`, but several actuation paths were
written against Windows binaries with no platform guard at all. Three were found
and fixed, and each failed differently — which is the useful part.

**`vision_engine.py` launched `notepad.exe` and killed the whole task.** A bare
`subprocess.Popen(["notepad.exe"])` inside `execute_visual_task()`. On Linux it
raised `FileNotFoundError`, and because nothing caught it, the exception
propagated out and discarded the entire visual action — screenshot, UI scan,
policy gate, actuation and reflection. Loud, and caught by a test. Now resolves
a real editor via `shutil.which()`, and treats "none found" as a skipped step.

**`action_registry.py` reported success when nothing launched — twice.** The
terminal branch ran `cmd.exe` and returned `{"status": "SUCCESS"}` regardless.
Reproduced:

```
/c: 1: cmd.exe: not found
terminal   -> {'status': 'SUCCESS', 'app': 'Terminal'}
```

The VS Code branch had the same shape, and it was arguably worse because
`shutil.which("code")` *was* already being called there — its answer was then
thrown away by an `or "code"` fallback that handed `Popen` a bare name that need
not exist:

```
.: 1: code: not found
vscode -> {'status': 'SUCCESS', 'app': 'VS Code', 'path': '.'}
```

These are more dangerous than the `notepad.exe` crash. A false success gives
nothing downstream any reason to doubt it, so a workflow continues as though a
terminal or an editor were open. No test covered `OpenAppAction` at all, which
is how both branches survived. Both now return `NOT_SUPPORTED`.

`shell=True` with a list argument was wrong in all three places. On POSIX it
makes the first element the command and the rest shell arguments, which is why
the errors above were attributed to `/c` and `.` rather than to the missing
binaries — the diagnostics pointed away from the actual cause.

**One failure labelled environmental was not.** `test_power_and_cdp_guards.py`
was counted as Windows-only code that cannot run on Linux. `KeepAwakeGuard` is
in fact correct — `activate()` and `deactivate()` both check `self.is_windows`
and return early elsewhere, and a separate test covers that path and passes.
The test died before reaching any of it, because
`patch("ctypes.windll.kernel32.SetThreadExecutionState")` cannot resolve a path
whose first element does not exist. Note that `create=True` does not fix that at
depth: it creates the final attribute only. The patch has to target
`ctypes.windll` itself and let `MagicMock` supply the chain, and the test must
also force `is_windows` on, or the guard returns early and the mock is never
called.

The lesson generalises: **a failure attributed to the platform deserves a
second look, because "this needs Windows" and "this test never ran" look
identical from the failure list.** Two of the three platform bugs above were
found by reading the code behind a failure that had already been categorised and
set aside.

### New: stop and ask instead of guessing

OpenAI led its GPT-6 Astra announcement with this behaviour. In the company's
own side-by-side, GPT-5.6 Sol autonomously built a personal career website in 13
minutes 15 seconds; Astra paused after 20 seconds to ask what career the user
was moving into. Sol's output was not so much wrong as unanchored — thirteen
minutes of confident work aimed at a guess.

Alfred had no equivalent. An ambiguous instruction went straight into the tool
loop, and whatever the model inferred became the answer. The only trace of the
idea anywhere in the tree was one log string in `initiative_engine.py:70`.

`agentic/clarifier.py` adds `ClarificationGate`, wired into `AgentHarness.run()`
before any tool is touched. The hard part is the restraint, so it fires only
when **both** hold:

1. The action is irreversible or externally visible — it deletes, sends,
   publishes, or spends.
2. The target or recipient is not actually named — only referred to by pronoun
   or vague quantifier ("it", "them", "the old ones").

Read-only work never fires it; asking "which files?" before listing files would
be absurd. Fully-specified destructive work never fires it either —
`delete build/ and dist/` says what it means and runs. An agent that asks about
everything is worse than one that guesses, because every question is an
interruption the user did not budget for.

The checks are deterministic and offline on purpose: testable without a model,
and identical every run. A gate that asks on Tuesday and not Wednesday is worse
than none, because the user cannot form an expectation of it.

A new `RunStatus.NEEDS_INPUT` is in `TERMINAL_STATUSES` but deliberately **not**
in `_FAILURE_STATUSES`. Pausing to ask is not failing, and counting it as a
failure would let an orchestration report treat a correct question as a broken
run.

It is off by default and threaded through `Orchestrator`, so nothing changes for
existing callers. It is turned on in the three places a human is present to
answer -- `run`, `talk`, and `AlfredRuntime` (via
`RuntimeConfig.ask_when_ambiguous`) -- and `--no-ask` turns it off in the two
commands, because an orchestrator running unattended has nobody to answer and a
question nobody can answer is not a pause, it is a stall.

**Wiring it into the voice agent nearly shipped a worse bug than the one being
fixed.** Before turning it on there, I checked what a returned question would
actually do, and `_speak_run()` had no case for it. A run that stops to ask is
not `ok`, and `NEEDS_INPUT` is deliberately absent from `_FAILURE_STATUSES`, so
`failed` is empty too. The function fell through to:

    error = result.get("error") or (result.get("failed") or ["something"])[0]
    return f"That did not work: {str(error)[:120]}"

The agent would have said, verbatim, *"That did not work: something"* -- while
holding a good question it never asked. A stall reported as an error, with the
useful part discarded: strictly worse than having no gate at all.

So the voice path learned to speak a question first. `OrchestrationReport`
gained a `clarifications` property, surfaced separately from `failed` because
asking is not failing, and included in `to_dict()` because the voice loop only
ever sees the dict -- without that hop the question would not survive the
boundary. `_speak_run()` speaks it, in a branch placed before the `ok` check.

Verified through the real `AlfredRuntime._make_runner()`, not a stand-in:

```
ask_when_ambiguous=True  -> 'Which ones exactly? I would rather ask than delete
                             something you wanted kept.'
                              ok=False failed=[] clarifications=1
ask_when_ambiguous=False -> 'Done. 1 step finished.'
                              ok=True  failed=[] clarifications=0
```

The general lesson is the one that mattered: a feature is not wired until the
*consumer* can handle what it produces. Passing the gate down was easy; the
silent stall was in the code that receives its output.

Verified live from the command line, both directions:

```
$ python -m jarvisx.agentic run "delete the old logs" --backend offline
node execute attempt 1 -> needs_input (None)
Result
## execute (generalist)
Which ones exactly? I would rather ask than delete something you wanted kept.

$ python -m jarvisx.agentic run "delete the old logs" --backend offline --no-ask
Result
## execute (generalist)
Completed 'delete the old logs'. 4 messages in transcript, 7 tools available.
```

31 tests, weighted as heavily toward the cases that must **not** trigger as
toward the ones that must. Two bugs were caught writing them: my own new
`trace.emit(kind=...)` collided with `TraceRecorder.emit()`'s positional `kind`
parameter, and the gate shipped unreachable until `Orchestrator` threaded it
down — a capability no code path reaches being the same defect as the dead
chess, DSA and VS Code routes fixed above.

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

- **11** orchestrators → 1. `agentic/scheduler.py::Orchestrator` is the strongest
  candidate: it has budgets, a policy gate, tracing, verification and 584
  passing tests behind it.
- 3 event buses → 1. 3 mission executors → 1. 4 capability registries → 1.

Do this behind the test suite, one concept at a time, and expect the file count
to drop by hundreds. This is the single biggest reduction in "where could this
bug be hiding".

**The count in the duplication table above says 12; the verified number is 11.**
Counting `^class .*Orchestrator` across `src/` gives eleven. The twelfth was
most likely `OrchestrationReport`, which is a result dataclass rather than an
orchestrator, or a test-only class. Worth correcting before anyone plans the
merge against the wrong number.

Reachability was measured rather than assumed — "external files" counts files
outside the class's own module that mention it:

| Class | Lines | External files |
|---|---|---|
| `Orchestrator` (`agentic/scheduler.py`) | 300 | **52** |
| `DynamicOrchestrator` | 1043 | **23** |
| `LinuxDevOpsOrchestrator` | 133 | 3 |
| `MetaOrchestrator` | 110 | 3 |
| `MultiAgentOrchestrator` | 48 | 2 |
| `SwarmOrchestrator` | 183 | 1 (its own test) |
| `AOVOrchestratorBridge` | 97 | 1 |
| `EventOrchestrator` | 20 | 1 |
| `FreeLLMIntentOrchestrator` | 141 | **0** |
| `UnifiedMeshOrchestrator` | 199 | **0** |
| `AmbientSovereignOrchestrator` | 171 | **0** |

Two carry the actual load. Three — 511 lines — are referenced by nothing at all
and could be deleted without touching a caller, which is the cheapest first
step and a useful test of whether the rest of the plan holds.

This is recorded as analysis, not done. Deleting orchestrators is destructive
and needs a decision rather than a heuristic; Phase 3 below says the same about
the unwired files.

### Phase 3 — Decide the fate of the unwired files

**Do not act on the number 22 in this section's original title.** I re-measured
reachability before treating it as a deletion list, and it does not hold up.

Parsing every file in `src/`, `tests/` and the repo root with `ast` and building
the first-party import graph gives **95 modules that nothing imports
statically**, not 22. My first pass at this reported 145; that was a bug in the
measuring script, which had a `pass` where the `from pkg import name` case
should have been handled, so it silently recorded nothing for that form of
import. The 95 is the corrected figure. I do not know how 22 was originally
derived, and I am not going to present either number as authoritative.

More important than which count is right: **no static analysis can prove a file
here is unreachable.** Seven call sites load modules by computed name or file
path:

```
skills/skill_loader.py:22            spec_from_file_location
skills/skill_sandbox.py:49           spec_from_file_location
skills/skill_discovery.py:45         import_module(candidate_pkg)
engineering/dynamic_tool_forge.py:259,292   spec_from_file_location
kernel/metamorphic_core.py:26        import_module(module_name)
orchestration/unified_agent_fleet.py:359    import_module(module_path)
```

A skills loader, a tool forge and a plugin fleet are exactly the subsystems
whose whole purpose is to import things that have no static importer. So a file
appearing on a "referenced by nothing" list is a prompt to investigate, never
evidence that it is dead. Deleting from that list would risk removing code that
only ever runs through a dynamic loader.

The rule for this phase is therefore unchanged and now better founded: **not
deletion by heuristic.** For each candidate, **wire it, or delete it on
purpose**, having checked whether any of the seven dynamic loaders can reach
it.
The obvious first candidate is `voice/eevee_live.py` — a real Gemini Live
duplex voice implementation that nothing calls, for the exact voice this
project was asked for. Wiring it is a feature; deleting it is a decision. Both
are better than leaving it.

### Phase 4 — Withdrawn: the numbers behind it were wrong

This phase was written on the strength of two counts, both of which I have now
measured properly. **Neither holds, and the premise largely does not exist.**

The claim was *136 places in `src/` assert their own completeness*. Grepping for
the actual claim shapes finds five matches, and **none of them is a file grading
itself**:

| File | What the match actually is |
|---|---|
| `friday/persistence.py:148` | a seeded *user goal* string |
| `orchestration/agent_worker.py:114` | an *instruction to a model*: "Write production-ready code" |
| `tools/test_voice.py:16` | a `print()` in a manual test script |
| `organism.py:122` | persona prompt text |
| `mesh/rag_ingestor.py:180` | a runtime progress line, "✅ INGESTION COMPLETE" |

Comment lines of the form `# Status: ...` or `# State: ...` — the shape a real
self-grade would take — number **zero**. The original 136 was counting prompt
text, persona strings and print statements as though each were a claim about the
file it sat in.

The companion claim was *84 files carry `simulate`/`mock`/`fake`/`placeholder`
markers*. That count was too low, not too high: **102** files match. But the
number is misleading in the other direction — 63 of them mention one of those
words only in a comment or docstring, and exactly **four** define anything named
that way:

    evolution_simulator.py:24    def simulate_upgrade
    prediction_engine.py:16      def simulate_trajectory
    telephony/remote_uplink.py:38  def simulate_incoming_message
    voice/desktop_gui_app.py:260   def simulate_double_clap

Two are legitimately simulators by nature; two are test helpers. None is a
stubbed-out feature pretending to be real.

**So Phase 4 is withdrawn rather than done.** It was the clearest case in this
audit of a conclusion outrunning its evidence, and it is worth keeping visible:
an audit is a document of claims, and this one made the same error it was
written to criticise. If self-grading is real in this codebase it is in the
`ev_*` GUI modules and the demo scripts, where "COMPLETE" appears in printed
output rather than in a claim about implementation state — which is a much
smaller and much less alarming problem than 136 unverified assertions.

The useful part of the original idea survives: the `doctor` pattern in
`agentic/` already probes a capability and reports `OK` or `--` based on
actually calling it. Extending that to the capabilities that matter is still
worth doing. It is just not the 136-claim cleanup this section described.

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
budgets, a policy gate, verification and tracing, and 584 tests pass against it.

The problems are **duplication** (eleven orchestrators — this count verified
exact) and **unwired real code**. On the second, the honest number is now
qualified rather than clean: 180 modules are reachable from neither a declared
entry point nor the test suite, but that figure is an upper bound on dead code
and not a list of it, because seven sites in this codebase load modules by
computed name or path. None of this is fixed by deleting files, which is why I
deleted four and stopped.

A third problem was listed here — unverified claims, "136 self-graded, 84
simulated" — and I have withdrawn it. Measured properly, the 136 was prompt
text and print statements, not files grading themselves; the real count of
genuine self-grades is zero. See the Phase 4 section. The correction matters
more than the phase would have: it is the audit's own claim, made with the same
confidence and the same lack of checking that the audit was written to call
out.

And the one thing that matters most cannot be done in this sandbox: nobody has
yet run this against a real model on a real machine with a real microphone.
That is Phase 1, and it should happen before anything else on this list.
