# Repository Cleanup Log

As part of **Phase Ω — Jarvis X Production Polish**, the repository underwent a comprehensive audit and cleanup to remove dead code, testing artifacts, and duplicate implementations.

## Deletions

### 1. Temporary Databases
- `test_console_*.db`
- `test_console_pause_*.db`
- `test_demo_*.db`
- `debug*.db`
- `test_q.db`
- `test_scratch.db`
- `op.db`

### 2. Debugging & Output Artifacts
- `debug_*.py`
- `pytest_out*.txt`
- `debug*_err.txt`, `debug*_out.txt`
- `dashboard_errors.txt`
- `.coverage`
- `test-results.xml`

### 3. Demo & Testing Scripts (Obsolete)
- `jarvis_test_runner.py`
- `proof_generator.py`
- `demo_architecture.py`
- `demo_bg.db`
- `demo_browser_auto.py`
- `demo_desktop_env.py`
- `demo_memory_adapter.py`
- `demo_omniroute.py`
- `demo_system.py`
- `test_embodiment.py`, `test_llm.py` (redundant stubs)
- `visual_agent.py` (legacy stub)
- `dummy_1/` directory

### 4. Reorganized Files
The following essential demos were moved to `examples/` for reference and regression testing:
- `demo_alpha.py`
- `demo_real_voice.py`
- `demo_phase19_vision.py`

*Repository is now clean and strictly adheres to the one source-of-truth located in `src/jarvisx`.*
