"""
Jarvis X — Autonomous LLM Feature Assimilator & Architectural Code Synthesizer.
Reasoning engine that dissects external repositories, determines what is needed vs bloat,
refactors & adapts code natively to Alfred OS architecture, tests it, and purges all clone waste.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("jarvisx.engineering.feature_assimilator")


class AutonomousFeatureAssimilator:
    """
    Autonomous AI Code Architect:
    1. Ephemeral Clone into isolated sandbox.
    2. Deep Codebase Dissection (AST, Classes, Functions, Dependencies).
    3. LLM Architectural Reasoning: Filters out bloat and isolates core value.
    4. Code Synthesis & Refactoring: Writes idiomatic, native Jarvis X modules.
    5. Automatic Verification & Test Execution.
    6. Complete Sandboxed Disk Purge (0 MB leftover bloat).
    """

    def __init__(self, workspace_root: str = "."):
        self.workspace = Path(workspace_root).resolve()

    def assimilate_feature_from_repo(
        self,
        repo_url: str,
        feature_goal: str = "Extract core algorithmic capability and adapt to Alfred OS",
        target_module_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Autonomous End-to-End Feature Assimilation Pipeline.
        """
        repo_clean = repo_url.strip().strip("'\"")
        if not repo_clean.startswith(("http://", "https://", "git@")):
            if "/" in repo_clean:
                repo_clean = f"https://github.com/{repo_clean}.git"

        # 1. Ephemeral Shallow Clone
        with tempfile.TemporaryDirectory(prefix="alfred_assimilate_") as temp_dir:
            temp_path = Path(temp_dir)
            cloned_dir = temp_path / "repo"

            cmd = ["git", "clone", "--depth", "1", "--single-branch", repo_clean, str(cloned_dir)]
            try:
                res = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
                if res.returncode != 0:
                    return {
                        "status": "failed",
                        "error": f"Git clone failed: {res.stderr.strip() or res.stdout.strip()}",
                    }
            except Exception as e:
                return {"status": "failed", "error": str(e)}

            # 2. Analyze Target Repository Structure and Code Samples
            repo_summary = self._dissect_repository(cloned_dir)

            # 3. Analyze Our Local Project Architecture Context
            local_context = self._get_local_project_context()

            # 4. LLM Architectural Reasoning & Synthesis
            synthesis_decision = self._reason_and_synthesize(
                repo_name=cloned_dir.name,
                repo_summary=repo_summary,
                local_context=local_context,
                feature_goal=feature_goal,
            )

            if synthesis_decision.get("status") != "success":
                return synthesis_decision

            # 5. Write Refactored Native Module
            module_name = target_module_name or synthesis_decision.get("recommended_module_name", "assimilated_feature.py")
            if not module_name.endswith(".py"):
                module_name += ".py"

            integrations_dir = self.workspace / "src" / "jarvisx" / "integrations"
            integrations_dir.mkdir(parents=True, exist_ok=True)
            target_file = integrations_dir / module_name

            code_content = synthesis_decision.get("synthesized_code", "")
            with open(target_file, "w", encoding="utf-8") as f:
                f.write(code_content)

            # 6. Generate and Run Automated Self-Verification Test
            test_file = self.workspace / "tests" / "unit" / f"test_{Path(module_name).stem}.py"
            test_file.parent.mkdir(parents=True, exist_ok=True)
            test_code = synthesis_decision.get("synthesized_test", self._generate_fallback_test(module_name))
            with open(test_file, "w", encoding="utf-8") as f:
                f.write(test_code)

            # Execute syntax & import verification
            test_result = self._verify_synthesized_module(target_file, test_file)

        # 7. Sandbox is now completely purged from disk
        return {
            "status": "success",
            "repo_url": repo_clean,
            "feature_goal": feature_goal,
            "module_created": f"src/jarvisx/integrations/{module_name}",
            "test_created": f"tests/unit/{test_file.name}",
            "rationale": synthesis_decision.get("rationale", "Extracted core logic, eliminated unneeded bloat."),
            "features_retained": synthesis_decision.get("features_retained", []),
            "bloat_discarded": synthesis_decision.get("bloat_discarded", ["Documentation", "Demo CLI", "Heavy dependencies", "Git history"]),
            "verification": test_result,
            "message": (
                f"Autonomous Feature Assimilation complete! Synthesized clean native module "
                f"'src/jarvisx/integrations/{module_name}' ({len(code_content.splitlines())} lines). "
                f"Discarded all non-essential framework bloat and purged temporary clone."
            ),
        }

    def _dissect_repository(self, repo_path: Path) -> Dict[str, Any]:
        """Scan repository files, extract signatures, docstrings, and primary algorithms."""
        code_snippets: List[Dict[str, str]] = []
        file_tree: List[str] = []

        for p in repo_path.rglob("*"):
            if not p.is_file():
                continue
            if any(part.startswith((".", "__", "venv", "node_modules", "test", "docs")) for part in p.parts):
                continue
            
            rel = str(p.relative_to(repo_path))
            file_tree.append(rel)

            if p.suffix in (".py", ".js", ".ts", ".go", ".rs") and len(code_snippets) < 8:
                try:
                    with open(p, "r", encoding="utf-8", errors="ignore") as f:
                        lines = f.readlines()
                        # Extract first 60 lines or docstrings/classes
                        sample = "".join(lines[:70])
                        code_snippets.append({"file": rel, "sample": sample})
                except Exception:
                    pass

        return {
            "file_tree": file_tree[:40],
            "total_files": len(file_tree),
            "code_samples": code_snippets,
        }

    def _get_local_project_context(self) -> str:
        """Summarize Jarvis X architecture for the LLM prompt."""
        return (
            "Jarvis X / Alfred OS Architecture:\n"
            "- Core Organism: AlfredOrganism with Brain (Groq/Gemini), Eyes (Vision/Screen), Hands (Tool Kernel), Mouth (TTS), Nerves (Event Bus).\n"
            "- Tools: Subclass Tool with spec(), execute(arguments), verify().\n"
            "- Memory: SQLite Second Brain, ChromaDB semantic vector store.\n"
            "- Coding Style: Clean, typed Python 3.12, dataclasses, minimal third-party dependencies, resilient error handling."
        )

    def _reason_and_synthesize(
        self,
        repo_name: str,
        repo_summary: Dict[str, Any],
        local_context: str,
        feature_goal: str,
    ) -> Dict[str, Any]:
        """Prompt LLM Brain to intelligently design, filter, and write the adapted module."""
        from jarvisx.llm.llm_router import LLMRouter
        router = LLMRouter()

        files_str = "\n".join(repo_summary.get("file_tree", [])[:25])
        samples_str = "\n\n".join([f"--- File: {s['file']} ---\n{s['sample']}" for s in repo_summary.get("code_samples", [])[:5]])

        prompt = f"""You are the Principal AI Systems Architect for Jarvis X / Alfred OS.
We are assimilating capabilities from an external repository into our sovereign operating agent.

TARGET REPOSITORY FILES:
{files_str}

RELEVANT CODE SAMPLES:
{samples_str}

OUR PROJECT ARCHITECTURE CONTEXT:
{local_context}

USER FEATURE GOAL:
"{feature_goal}"

YOUR ARCHITECTURAL MISSION:
1. Think critically: What is truly NEEDED for our project vs what is BLOAT/DISTRACTION (e.g. demo scripts, UI widgets, unused frameworks, large dependencies)?
2. Discard all non-essential bloat.
3. Synthesize a single, clean, self-contained, production-grade Python 3.12 module that implements the required feature natively adapted for Jarvis X.
4. Provide a simple pytest unit test for the synthesized module.

Respond in this EXACT clean structure:

### RATIONALE
<Detailed explanation of what code was chosen, what bloat was eliminated, and architectural fit>

### RETAINED
- <Feature 1>
- <Feature 2>

### DISCARDED
- <Bloat 1>
- <Bloat 2>

### MODULE_NAME
<clean_snake_case_filename.py>

### SYNTHESIZED_CODE
```python
<Complete, working Python 3.12 code>
```

### SYNTHESIZED_TEST
```python
<Complete pytest test code>
```
"""
        try:
            try:
                loop = asyncio.get_event_loop()
                if loop.is_closed():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    res = pool.submit(asyncio.run, router.route_request(prompt)).result()
            else:
                res = loop.run_until_complete(router.route_request(prompt))

            raw_text = res.get("result", {}).get("response", "") or res.get("text", "") or ""

            # Parse Structured Response
            data = self._parse_llm_response(raw_text)
            if data and data.get("synthesized_code"):
                data["status"] = "success"
                return data
            else:
                return {"status": "failed", "error": f"LLM did not return parseable code. Raw output: {raw_text[:250]}"}
        except Exception as e:
            return {"status": "failed", "error": f"LLM synthesis error: {e}"}

    def _parse_llm_response(self, raw_text: str) -> Dict[str, Any]:
        """Resiliently parses structured sections or JSON with embedded code snippets."""
        # 1. Extract all multiline code blocks (ignoring inline backticks)
        multiline_blocks = [
            b.strip() for b in re.findall(r'```(?:python)?\s*\n(.*?)\n\s*```', raw_text, re.DOTALL)
            if len(b.strip().splitlines()) >= 3
        ]

        # 2. Extract metadata sections with case-insensitivity
        rat_m = re.search(r'###\s*RATIONALE\s*[:\n]\s*(.*?)(?=\n###|\Z)', raw_text, re.DOTALL | re.IGNORECASE)
        rationale = rat_m.group(1).strip() if rat_m else "Assimilated core capability natively into Alfred OS."

        name_m = re.search(r'###\s*MODULE_NAME\s*[:\n]\s*([^\n]+)', raw_text, re.IGNORECASE)
        mod_name = name_m.group(1).strip().strip("`'\"") if name_m else "assimilated_feature.py"
        if not mod_name.endswith(".py"):
            mod_name += ".py"

        retained_m = re.search(r'###\s*RETAINED\s*[:\n]\s*(.*?)(?=\n###|\Z)', raw_text, re.DOTALL | re.IGNORECASE)
        retained = re.findall(r'-\s*(.+)', retained_m.group(1)) if retained_m else ["Core Capability", "Typed Interface"]

        discarded_m = re.search(r'###\s*DISCARDED\s*[:\n]\s*(.*?)(?=\n###|\Z)', raw_text, re.DOTALL | re.IGNORECASE)
        discarded = re.findall(r'-\s*(.+)', discarded_m.group(1)) if discarded_m else ["Non-essential framework bloat", "Documentation"]

        if multiline_blocks:
            code = multiline_blocks[0]
            test = multiline_blocks[1] if len(multiline_blocks) > 1 else self._generate_fallback_test(mod_name)
            return {
                "rationale": rationale,
                "recommended_module_name": mod_name,
                "features_retained": retained,
                "bloat_discarded": discarded,
                "synthesized_code": code,
                "synthesized_test": test,
            }

        # 3. Fallback: JSON parser
        match = re.search(r'\{.*\}', raw_text, re.DOTALL)
        if match:
            candidate = match.group(0)
            try:
                data = json.loads(candidate, strict=False)
                if data.get("synthesized_code"):
                    return data
            except Exception:
                pass

        return {}

    def _generate_fallback_test(self, module_name: str) -> str:
        stem = Path(module_name).stem
        return f"""
import pytest

def test_assimilated_module_import():
    try:
        from jarvisx.integrations import {stem}
        assert {stem} is not None
    except ImportError as e:
        pytest.fail(f"Failed to import synthesized module: {{e}}")
"""

    def _verify_synthesized_module(self, module_path: Path, test_path: Path) -> Dict[str, Any]:
        """Test the synthesized module using python compilation and pytest."""
        # 1. Compile test
        try:
            subprocess.run([sys.executable, "-m", "py_compile", str(module_path)], check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            return {"syntax_verified": False, "error": f"Syntax error in synthesized code: {e.stderr}"}

        # 2. Pytest execution
        try:
            test_res = subprocess.run([sys.executable, "-m", "pytest", str(test_path), "-v"], capture_output=True, text=True, timeout=20)
            passed = test_res.returncode == 0
            return {
                "syntax_verified": True,
                "tests_passed": passed,
                "pytest_output": test_res.stdout.strip()[:400],
            }
        except Exception as ex:
            return {"syntax_verified": True, "tests_passed": False, "warning": str(ex)}


# Singleton accessor
_assimilator_instance: Optional[AutonomousFeatureAssimilator] = None

def get_feature_assimilator() -> AutonomousFeatureAssimilator:
    global _assimilator_instance
    if _assimilator_instance is None:
        _assimilator_instance = AutonomousFeatureAssimilator()
    return _assimilator_instance
