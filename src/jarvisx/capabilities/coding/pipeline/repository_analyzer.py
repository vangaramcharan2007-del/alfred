from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, List, Optional

@dataclass
class RepositoryProfile:
    language: str
    framework: str
    architecture_style: str
    entry_points: List[str] = field(default_factory=list)
    important_files: List[str] = field(default_factory=list)
    root_path: str = ""
    files_count: int = 0
    has_tests: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "language": self.language,
            "framework": self.framework,
            "architecture_style": self.architecture_style,
            "entry_points": self.entry_points,
            "important_files": self.important_files,
            "root_path": self.root_path,
            "files_count": self.files_count,
            "has_tests": self.has_tests
        }

@dataclass
class RepositoryContext:
    root_path: str
    primary_language: str
    framework: str
    files_count: int
    key_files: List[str] = field(default_factory=list)
    has_tests: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    profile: Optional[RepositoryProfile] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "root_path": self.root_path,
            "primary_language": self.primary_language,
            "framework": self.framework,
            "files_count": self.files_count,
            "key_files": self.key_files,
            "has_tests": self.has_tests,
            "metadata": self.metadata
        }
        if self.profile:
            d["profile"] = self.profile.to_dict()
        return d

class RepositoryAnalyzer:
    def generate_profile(self, repo_path: str) -> RepositoryProfile:
        ctx = self.analyze(repo_path)
        return ctx.profile or RepositoryProfile(
            language=ctx.primary_language,
            framework=ctx.framework,
            architecture_style="Modular",
            entry_points=ctx.key_files,
            important_files=ctx.key_files,
            root_path=ctx.root_path,
            files_count=ctx.files_count,
            has_tests=ctx.has_tests
        )

    def analyze(self, repo_path: str) -> RepositoryContext:
        p = Path(repo_path)
        if not p.exists() or not p.is_dir():
            prof = RepositoryProfile(
                language="unknown",
                framework="none",
                architecture_style="Unknown",
                entry_points=[],
                important_files=[],
                root_path=str(repo_path),
                files_count=0,
                has_tests=False
            )
            return RepositoryContext(
                root_path=str(repo_path),
                primary_language="unknown",
                framework="none",
                files_count=0,
                key_files=[],
                has_tests=False,
                profile=prof
            )

        key_files: List[str] = []
        entry_points: List[str] = []
        py_files = 0
        js_files = 0
        ts_files = 0
        java_files = 0
        total_files = 0
        has_tests = False

        for f in p.rglob("*"):
            if f.is_file() and not any(part.startswith(".") or part in ["__pycache__", "node_modules", "venv", "target", "dist"] for part in f.parts):
                total_files += 1
                rel_str = str(f.relative_to(p))
                fname = f.name.lower()
                
                if fname in ["pyproject.toml", "requirements.txt", "package.json", "pom.xml", "build.gradle", "main.py", "app.py", "index.js", "index.ts", "application.java", "dockerfile"]:
                    key_files.append(rel_str)
                if fname in ["main.py", "app.py", "index.js", "index.ts", "server.js", "app.js", "application.java"]:
                    entry_points.append(rel_str)
                if "test" in fname or "tests" in rel_str.lower():
                    has_tests = True

                if f.suffix == ".py":
                    py_files += 1
                elif f.suffix in [".js", ".jsx"]:
                    js_files += 1
                elif f.suffix in [".ts", ".tsx"]:
                    ts_files += 1
                elif f.suffix == ".java":
                    java_files += 1

        lang_counts = {"Python": py_files, "JavaScript": js_files, "TypeScript": ts_files, "Java": java_files}
        primary_lang = max(lang_counts, key=lang_counts.get) if max(lang_counts.values()) > 0 else "generic"

        framework = "none"
        if primary_lang == "Python":
            for k in key_files + [f.name for f in p.glob("*.py")]:
                full_f = p / k
                if full_f.is_file():
                    try:
                        content = full_f.read_text(encoding="utf-8", errors="ignore").lower()
                        if "fastapi" in content:
                            framework = "FastAPI"
                            break
                        elif "flask" in content:
                            framework = "Flask"
                            break
                        elif "django" in content:
                            framework = "Django"
                            break
                    except Exception:
                        pass
            if framework == "none" and py_files > 0:
                framework = "Python Standard"
        elif primary_lang in ["JavaScript", "TypeScript"]:
            pkg = p / "package.json"
            if pkg.exists():
                try:
                    content = pkg.read_text(encoding="utf-8", errors="ignore").lower()
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
            else:
                framework = "Node.js"
        elif primary_lang == "Java":
            for f in p.rglob("*.java"):
                try:
                    content = f.read_text(encoding="utf-8", errors="ignore")
                    if "SpringBootApplication" in content or "org.springframework" in content:
                        framework = "Spring Boot"
                        break
                except Exception:
                    pass
            if framework == "none":
                framework = "Java Standard"

        arch_style = "REST API" if framework in ["FastAPI", "Express", "Flask", "Spring Boot"] else ("Fullstack Web" if framework in ["Next.js", "Django", "React"] else "Modular Monolith")

        profile = RepositoryProfile(
            language=primary_lang.lower(),
            framework=framework,
            architecture_style=arch_style,
            entry_points=entry_points or key_files,
            important_files=key_files,
            root_path=str(p.resolve()),
            files_count=total_files,
            has_tests=has_tests
        )

        return RepositoryContext(
            root_path=str(p.resolve()),
            primary_language=primary_lang.lower(),
            framework=framework,
            files_count=total_files,
            key_files=key_files,
            has_tests=has_tests,
            profile=profile
        )
