# Deployment Instructions - Workforce Layer

## 1. Installation
We use external dependency installation to avoid git submodules.

```bash
# Inside Jarvis X root
pip install agent-orchestrator

# Ensure git worktree base directories exist
mkdir -p /tmp/jarvisx_worktrees
```

## 2. Configuration
Ensure the Agent Orchestrator configuration points to your local LLM inference engines (e.g., Ollama, vLLM) in the environment file:
```env
# .env
AGENT_ORCHESTRATOR_LLM_URL="http://localhost:11434"
```

## 3. Database Migration
The `workforce_tasks` persistence layer uses SQLite WAL.
Run the initialization script:
```python
from src.jarvisx.core.workforce_db import WorkforceDatabase
db = WorkforceDatabase("var/workforce.db")
```

## Rollback Strategy
If Agent Orchestrator exhibits unstable behavior, Hermes routing can be instantly reverted via the `ENABLE_WORKFORCE` feature toggle.

If disabled:
1. `reasoning_bus.py` defaults all software engineering tasks back to `single_agent` mode.
2. `git_worktree_manager.py` purges all active temporary worktrees.
3. Alfred resumes legacy inline execution.
