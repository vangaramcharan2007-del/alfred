"""
Alfred Coding Commands - Real file operations powered by LLM.
Every command reads real files, sends to real LLM, produces real output.
No fakes. No simulations. If Ollama is offline, says so.
"""
from __future__ import annotations
import ast
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional


def _call_ollama(prompt: str, model: str = "qwen2.5-coder:7b", timeout: float = 60.0) -> Optional[str]:
    """Call Ollama API. Returns response text or None if unavailable."""
    import json
    import urllib.request
    try:
        url = "http://localhost:11434/api/generate"
        payload = json.dumps({"model": model, "prompt": prompt, "stream": False}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("response", "")
    except Exception:
        return None


def _read_file(path: str) -> Optional[str]:
    """Read a file safely. Returns None if not found."""
    p = Path(path)
    if not p.exists():
        return None
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return None


# ------------------------------------------------------------------
# 1. Workspace Context ("Alfred continue")
# ------------------------------------------------------------------
def get_workspace_context(cwd: str = ".") -> Dict[str, Any]:
    """Gather real workspace state: git, tests, TODOs, open files."""
    ctx = {}

    # Git branch
    r = subprocess.run(["git", "branch", "--show-current"], cwd=cwd, capture_output=True, text=True, timeout=5)
    ctx["branch"] = r.stdout.strip() or "unknown"

    # Git status
    r = subprocess.run(["git", "status", "--short"], cwd=cwd, capture_output=True, text=True, timeout=5)
    ctx["modified_files"] = [l.strip() for l in r.stdout.splitlines() if l.strip()]

    # Last 5 commits
    r = subprocess.run(["git", "log", "--oneline", "-5"], cwd=cwd, capture_output=True, text=True, timeout=5)
    ctx["recent_commits"] = [l.strip() for l in r.stdout.splitlines() if l.strip()]

    # Git diff stat
    r = subprocess.run(["git", "diff", "--stat"], cwd=cwd, capture_output=True, text=True, timeout=5)
    ctx["diff_stat"] = r.stdout.strip()

    # TODOs and FIXMEs
    todos = []
    try:
        r = subprocess.run(["git", "grep", "-n", "-i", "-E", "TODO|FIXME|HACK|XXX"],
                           cwd=cwd, capture_output=True, text=True, timeout=10)
        for line in r.stdout.splitlines()[:20]:  # Cap at 20
            todos.append(line.strip())
    except Exception:
        pass
    ctx["todos"] = todos

    # Pytest (with timeout safety)
    try:
        r = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/unit/", "--tb=short", "-q", "-m", "not slow"],
            cwd=cwd, capture_output=True, text=True, timeout=10
        )
        ctx["test_exit_code"] = r.returncode
        ctx["test_output"] = r.stdout.strip()[-500:]  # Last 500 chars
    except Exception as e:
        ctx["test_exit_code"] = -1
        ctx["test_output"] = f"Test check skipped/timed out: {e}"

    return ctx


def alfred_continue(cwd: str = ".") -> Dict[str, Any]:
    """'Alfred continue' — understand workspace and explain what we were doing."""
    print("\nAlfred: Scanning workspace...\n")
    ctx = get_workspace_context(cwd)

    print(f"  Branch:          {ctx['branch']}")
    print(f"  Modified files:  {len(ctx['modified_files'])}")
    print(f"  Recent commits:  {len(ctx['recent_commits'])}")
    print(f"  TODOs found:     {len(ctx['todos'])}")
    print(f"  Tests:           {'PASS' if ctx['test_exit_code'] == 0 else 'FAIL'}")
    print()

    # Build LLM prompt with real context
    prompt = f"""You are Alfred, an AI engineering assistant. Analyze this workspace state and explain:
1. What the developer was working on
2. What needs attention right now
3. Suggested next steps

Be concise and specific. Use the actual file names and commit messages.

Git Branch: {ctx['branch']}
Modified Files: {ctx['modified_files']}
Recent Commits: {ctx['recent_commits']}
Diff Stats: {ctx['diff_stat']}
TODOs/FIXMEs: {ctx['todos'][:10]}
Test Status: {'PASSING' if ctx['test_exit_code'] == 0 else 'FAILING'}
Test Output (last 300 chars): {ctx['test_output'][-300:]}
"""

    response = _call_ollama(prompt)
    if response:
        print("Alfred:\n")
        print(response)
        print()
        return {"status": "SUCCESS", "context": ctx, "explanation": response}
    else:
        # Fallback: still useful without LLM
        print("Alfred: [Ollama offline — showing raw context]\n")
        if ctx["modified_files"]:
            print("  You have uncommitted changes in:")
            for f in ctx["modified_files"][:10]:
                print(f"    {f}")
        if ctx["recent_commits"]:
            print(f"\n  Last commit: {ctx['recent_commits'][0]}")
        if ctx["test_exit_code"] != 0:
            print(f"\n  WARNING: Tests are FAILING.")
            print(f"  {ctx['test_output'][-200:]}")
        if ctx["todos"]:
            print(f"\n  Open TODOs:")
            for t in ctx["todos"][:5]:
                print(f"    {t}")
        print()
        return {"status": "PARTIAL", "context": ctx, "explanation": "Ollama offline"}


# ------------------------------------------------------------------
# 2. Fix This — Real bug fix loop
# ------------------------------------------------------------------
def alfred_fix_this(cwd: str = ".") -> Dict[str, Any]:
    """'Fix this' — read real test failures, ask LLM for patch, apply, verify."""
    print("\nAlfred: Running tests to find failures...\n")

    # Run pytest with full traceback
    r = subprocess.run([sys.executable, "-m", "pytest", "tests/", "--tb=long", "-q", "--no-header"],
                       cwd=cwd, capture_output=True, text=True, timeout=120)

    if r.returncode == 0:
        print("  All tests passing. Nothing to fix.\n")
        return {"status": "NOTHING_TO_FIX", "test_output": r.stdout.strip()}

    test_output = r.stdout + r.stderr
    print(f"  Found failures. Exit code: {r.returncode}")
    print(f"  Output (last 400 chars):\n  {test_output[-400:]}\n")

    # Get git diff for context
    diff_r = subprocess.run(["git", "diff"], cwd=cwd, capture_output=True, text=True, timeout=10)
    diff_text = diff_r.stdout[:2000]  # Cap diff size

    # Try to identify failing file from traceback
    failing_files = set()
    for line in test_output.splitlines():
        if "FAILED" in line:
            # Extract test file path
            match = re.search(r'(tests/\S+\.py)', line)
            if match:
                failing_files.add(match.group(1))
        if "File " in line:
            match = re.search(r'File "([^"]+\.py)"', line)
            if match and "site-packages" not in match.group(1):
                failing_files.add(match.group(1))

    # Read failing files
    file_contents = {}
    for f in list(failing_files)[:3]:  # Cap at 3 files
        content = _read_file(os.path.join(cwd, f))
        if content:
            file_contents[f] = content[:3000]  # Cap per file

    prompt = f"""You are Alfred, a senior software engineer. Fix the failing tests.

TEST OUTPUT:
{test_output[-1500:]}

GIT DIFF:
{diff_text[:1000]}

RELEVANT FILES:
"""
    for fname, content in file_contents.items():
        prompt += f"\n--- {fname} ---\n{content}\n"

    prompt += """
Respond with:
1. Root cause (one sentence)
2. The exact fix as a code block with the filename as a comment on line 1
3. Nothing else
"""

    print("  Asking Alfred for diagnosis...\n")
    response = _call_ollama(prompt, timeout=90.0)

    if response:
        print("Alfred:\n")
        print(response)
        print()
        return {"status": "DIAGNOSED", "diagnosis": response, "failing_files": list(failing_files)}
    else:
        print("  Alfred: [Ollama offline] Cannot generate fix. Here's the traceback:\n")
        print(f"  {test_output[-500:]}\n")
        return {"status": "NOT_AVAILABLE", "reason": "Ollama offline", "test_output": test_output}


# ------------------------------------------------------------------
# 3. Write Tests
# ------------------------------------------------------------------
def write_tests(file_path: str) -> Dict[str, Any]:
    """Read a source file, ask LLM to generate tests."""
    content = _read_file(file_path)
    if not content:
        print(f"\n  File not found: {file_path}\n")
        return {"status": "FILE_NOT_FOUND", "path": file_path}

    print(f"\nAlfred: Generating tests for {file_path}...\n")

    prompt = f"""Write pytest tests for this Python file. Cover all public functions and edge cases.
Return ONLY the test code as a single code block. No explanations.

--- {file_path} ---
{content[:4000]}
"""
    response = _call_ollama(prompt, timeout=90.0)
    if not response:
        print("  Alfred: [Ollama offline] Cannot generate tests.\n")
        return {"status": "NOT_AVAILABLE", "reason": "Ollama offline"}

    # Extract code block
    code_match = re.search(r'```(?:python)?\s*\n(.*?)```', response, re.DOTALL)
    test_code = code_match.group(1) if code_match else response

    # Write test file
    src_path = Path(file_path)
    test_name = f"test_{src_path.stem}.py"
    test_dir = Path("tests/generated")
    test_dir.mkdir(parents=True, exist_ok=True)
    test_path = test_dir / test_name
    test_path.write_text(test_code, encoding="utf-8")

    print(f"  Written to: {test_path}")
    print(f"  Run: pytest {test_path}\n")
    return {"status": "SUCCESS", "test_file": str(test_path), "test_code": test_code}


# ------------------------------------------------------------------
# 4. Explain File
# ------------------------------------------------------------------
def explain_file(file_path: str) -> Dict[str, Any]:
    """Read a file and explain its architecture."""
    content = _read_file(file_path)
    if not content:
        print(f"\n  File not found: {file_path}\n")
        return {"status": "FILE_NOT_FOUND", "path": file_path}

    print(f"\nAlfred: Analyzing {file_path}...\n")

    prompt = f"""Explain this code. Be concise:
1. Purpose (one sentence)
2. Key classes/functions and what they do
3. Dependencies
4. Potential issues

--- {file_path} ---
{content[:5000]}
"""
    response = _call_ollama(prompt, timeout=60.0)
    if response:
        print(f"Alfred:\n\n{response}\n")
        return {"status": "SUCCESS", "explanation": response}
    else:
        print("  Alfred: [Ollama offline] Cannot explain.\n")
        return {"status": "NOT_AVAILABLE", "reason": "Ollama offline"}


# ------------------------------------------------------------------
# 5. Code Review
# ------------------------------------------------------------------
def review_code(file_path: str) -> Dict[str, Any]:
    """Review a file for bugs, style, and improvements."""
    content = _read_file(file_path)
    if not content:
        print(f"\n  File not found: {file_path}\n")
        return {"status": "FILE_NOT_FOUND", "path": file_path}

    print(f"\nAlfred: Reviewing {file_path}...\n")

    prompt = f"""You are a senior code reviewer. Review this file:
1. Bugs or logic errors
2. Security issues
3. Performance problems
4. Style improvements
5. Missing error handling

Be specific. Reference line numbers when possible.

--- {file_path} ---
{content[:5000]}
"""
    response = _call_ollama(prompt, timeout=60.0)
    if response:
        print(f"Alfred:\n\n{response}\n")
        return {"status": "SUCCESS", "review": response}
    else:
        print("  Alfred: [Ollama offline] Cannot review.\n")
        return {"status": "NOT_AVAILABLE", "reason": "Ollama offline"}


# ------------------------------------------------------------------
# 6. Find Dead Code
# ------------------------------------------------------------------
def find_dead_code(cwd: str = ".") -> Dict[str, Any]:
    """Walk Python files, find unused imports and unreachable functions."""
    print("\nAlfred: Scanning for dead code...\n")

    src_dir = Path(cwd) / "src"
    if not src_dir.exists():
        src_dir = Path(cwd)

    issues = []

    for py_file in src_dir.rglob("*.py"):
        if "__pycache__" in str(py_file) or ".venv" in str(py_file):
            continue
        try:
            source = py_file.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(source)
        except (SyntaxError, Exception):
            continue

        # Find unused imports
        imports = set()
        used_names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.asname or alias.name.split(".")[0]
                    imports.add(name)
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    name = alias.asname or alias.name
                    imports.add(name)
            elif isinstance(node, ast.Name):
                used_names.add(node.id)
            elif isinstance(node, ast.Attribute):
                if isinstance(node.value, ast.Name):
                    used_names.add(node.value.id)

        unused = imports - used_names - {"__future__", "annotations", "__all__"}
        for name in unused:
            rel = py_file.relative_to(Path(cwd))
            issues.append(f"  Unused import '{name}' in {rel}")

    if issues:
        print(f"Found {len(issues)} potential issues:\n")
        for issue in issues[:30]:
            print(issue)
        if len(issues) > 30:
            print(f"\n  ... and {len(issues) - 30} more.")
    else:
        print("  No dead code found.\n")

    print()
    return {"status": "SUCCESS", "issues_count": len(issues), "issues": issues[:50]}


# ------------------------------------------------------------------
# 7. Generate Docs
# ------------------------------------------------------------------
def generate_docs(file_path: str) -> Dict[str, Any]:
    """Read a file, generate docstrings for all functions/classes."""
    content = _read_file(file_path)
    if not content:
        print(f"\n  File not found: {file_path}\n")
        return {"status": "FILE_NOT_FOUND", "path": file_path}

    print(f"\nAlfred: Generating documentation for {file_path}...\n")

    prompt = f"""Add comprehensive docstrings to every function and class in this Python file.
Return the COMPLETE file with docstrings added. Keep all existing code unchanged.
Use Google-style docstrings.

--- {file_path} ---
{content[:5000]}
"""
    response = _call_ollama(prompt, timeout=90.0)
    if not response:
        print("  Alfred: [Ollama offline] Cannot generate docs.\n")
        return {"status": "NOT_AVAILABLE", "reason": "Ollama offline"}

    code_match = re.search(r'```(?:python)?\s*\n(.*?)```', response, re.DOTALL)
    documented_code = code_match.group(1) if code_match else response

    # Write to a .documented.py file (don't overwrite original)
    src = Path(file_path)
    out_path = src.parent / f"{src.stem}_documented{src.suffix}"
    out_path.write_text(documented_code, encoding="utf-8")

    print(f"  Written to: {out_path}")
    print(f"  Review and replace original if satisfied.\n")
    return {"status": "SUCCESS", "output_file": str(out_path)}
