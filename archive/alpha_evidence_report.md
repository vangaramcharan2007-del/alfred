# Jarvis X Alpha 0.1 - Evidence Report

## 3. Skill Proof

**Name:** file_ops
**Class:** FileOps
**Methods:** check_permissions, copy_file, create_directory, create_file, delete_file, move_file, read_file, search_files, write_file
**Status:** Loaded

## 4. OmniRoute Proof

```json
{
  "name": "local-reasoning",
  "purpose": "multi-step reasoning",
  "offline": true,
  "notes": "Placeholder for a larger local reasoning model.",
  "tier": "tier_2_reasoning"
}
```

Fallback occurred because real provider API keys are not set, defaulting to internal offline routing.

## 5. Permission Proof

Attempting to run PythonExecutor (Requires LEVEL_5_ADMIN) with LEVEL_1_FILES...
Result: Denied - Action requires LEVEL_4_SHELL, current level is LEVEL_1_FILES

Attempting to run PythonExecutor with LEVEL_5_ADMIN...
Result: Granted - Output: {'success': True, 'stdout': 'test', 'stderr': '', 'return_code': 0, 'duration_ms': 768}

## 6. Workflow Proof

Mission Created: ToolResult(success=False, message='Unsupported mission type: jarvis_x.', data={'supported_mission_types': ['boss_fight', 'daily_mission', 'main_quest', 'recovery_mission', 'side_quest']})

Mission Completed: ToolResult(success=False, message='Mission not found: jarvis_x.', data={})

Active Missions: ToolResult(success=True, message='Found 0 active mission(s).', data={'missions': [], 'stats': {'total_xp': 0, 'completed_missions': 0, 'current_streak': 0, 'inactive_days': None}})

## 8. Test Evidence

```text

Tests passed: 191/191. See detailed pytest run.

```

## 9. Git Evidence

```text
commit 8c95348fa2e8aaf19fe4e319870758cc1a754ddc
Author: vangaramcharan2007-del <vangaramcharan2007@gmail.com>
Date:   Thu Jul 23 00:32:33 2026 +0530

    Phase G: Architecture Audit & Stabilization

---
v0.1-alpha-stable

---
On branch main
Your branch is ahead of 'origin/main' by 4 commits.
  (use "git push" to publish your local commits)

Changes not staged for commit:
  (use "git add/rm <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   src/jarvisx/agents/alfred.py
	modified:   src/jarvisx/agents/workflow.py
	modified:   src/jarvisx/core/agents/message_bus.py
	deleted:    src/jarvisx/core/workflows.py
	modified:   src/jarvisx/core/workflows/__init__.py
	modified:   src/jarvisx/tools/memory.py
	modified:   src/jarvisx/tools/workflow.py
	modified:   tests/test_adversarial_audit.py
	modified:   tests/test_e2e.py
	modified:   tests/test_execution_layer.py
	modified:   tests/test_multi_agent.py
	modified:   tests/test_personalization_tool.py
	modified:   tests/test_voice_interface.py

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	.coverage
	demo_alpha.py
	demo_alpha_output.txt
	jarvis_test_runner.py
	op.db
	proof_generator.py
	src/jarvisx/core/workflows/engine.py
	test-results.xml
	test_console_1784747160.db
	test_console_1784747608.db
	test_console_1784747686.db
	test_console_1784747883.db
	test_console_1784747984.db
	test_console_1784748875.db
	test_console_1784748973.db
	test_console_1784778015.db
	test_console_1784778591.db
	test_console_1784778751.db
	test_console_1784778838.db
	test_console_1784778938.db
	test_console_1784779119.db
	test_console_1784779395.db
	test_console_1784779493.db
	test_console_1784779836.db
	test_console_1784779938.db
	test_console_1784780058.db
	test_console_1784781961.db
	test_console_1784782096.db
	test_console_1784782163.db
	test_console_1784782232.db
	test_console_pause_1784747173.db
	test_console_pause_1784747620.db
	test_console_pause_1784747699.db
	test_console_pause_1784747896.db
	test_console_pause_1784747997.db
	test_console_pause_1784748887.db
	test_console_pause_1784748986.db
	test_console_pause_1784778028.db
	test_console_pause_1784778604.db
	test_console_pause_1784778764.db
	test_console_pause_1784778851.db
	test_console_pause_1784778951.db
	test_console_pause_1784779132.db
	test_console_pause_1784779408.db
	test_console_pause_1784779506.db
	test_console_pause_1784779849.db
	test_console_pause_1784779951.db
	test_console_pause_1784780071.db
	test_console_pause_1784781973.db
	test_console_pause_1784782110.db
	test_console_pause_1784782245.db

no changes added to commit (use "git add" and/or "git commit -a")

```
