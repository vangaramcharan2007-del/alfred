from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, List, Optional

@dataclass
class RepositoryContext:
    root_path: str
    primary_language: str
    framework: str
    files_count: int
    key_files: List[str] = field(default_factory=list)
    has_tests: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "root_path": self.root_path,
            "primary_language": self.primary_language,
            "framework": self.framework,
            "files_count": self.files_count,
            "key_files": self.key_files,
            "has_tests": self.has_tests,
            "metadata": self.metadata
        }

class RepositoryAnalyzer:
    def analyze(self, repo_path: str) -> RepositoryContext:
        p = Path(repo_path)
        if not p.exists() or not p.is_dir():
            return RepositoryContext(
                root_path=str(repo_path),
                primary_language="unknown",
                framework="none",
                files_count=0,
                key_files=[],
                has_tests=False
            )

        key_files: List[str] = []
        py_files = 0
        js_ts_files = 0
        total_files = 0
        has_tests = False

        for f in p.rglob("*"):
            if f.is_file() and not any(part.startswith(".") or part in ["__pycache__", "node_modules", "venv"] for part in f.parts):
                total_files += 1
                rel_str = str(f.relative_to(p))
                if f.name in ["pyproject.toml", "requirements.txt", "package.json", "main.py", "app.py", "Dockerfile"]:
                    key_files.append(rel_str)
                if "test" in f.name.lower() or "tests" in rel_str.lower():
                    has_tests = True
                if f.suffix in [".py"]:
                    py_files += 1
                elif f.suffix in [".js", ".ts", ".jsx", ".tsx"]:
                    js_ts_files += 1

        primary_lang = "python" if py_files >= js_ts_files else ("javascript/typescript" if js_ts_files > 0 else "generic")

        framework = "none"
        if primary_lang == "python":
            # Check for FastAPI / Flask
            for k in key_files + [f.name for f in p.glob("*.py")]:
                full_f = p / k
                if full_f.is_file():
                    try:
                        content = full_f.read_text(encoding="utf-8", errors="ignore")
                        if "fastapi" in content.lower():
                            framework = "FastAPI"
                            break
                        elif "flask" in content.lower():
                            framework = "Flask"
                            break
                        elif "django" in content.lower():
                            framework = "Django"
                            break
                    except Exception:
                        pass
            if framework == "none" and py_files > 0:
                framework = "Python Standard"
        elif primary_lang == "javascript/typescript":
            pkg = p / "package.json"
            if pkg.exists():
                try:
                    content = pkg.read_text(encoding="utf-8", errors="ignore")
                    if "next" in content:
                        framework = "Next.js"
                    elif "react" in content:
                        framework = "React"
                    elif "express" in content:
                        framework = "Express"
                    else:
                        framework = "Node.js"
                except Exception:
                    framework = "Node.js"

        return RepositoryContext(
            root_path=str(p.resolve()),
            primary_language=primary_lang,
            framework=framework,
            files_count=total_files,
            key_files=key_files,
            has_tests=has_tests
        )
