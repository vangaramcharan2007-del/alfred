from __future__ import annotations

import ast
import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Set


@dataclass
class RepositoryInfo:
    root_path: str
    languages: List[str] = field(default_factory=list)
    frameworks: List[str] = field(default_factory=list)
    package_manager: str = "Unknown"
    build_system: str = "Unknown"
    test_framework: str = "None detected"
    entry_points: List[str] = field(default_factory=list)
    dependency_graph: Dict[str, List[str]] = field(default_factory=dict)
    external_dependencies: List[str] = field(default_factory=list)
    ci_cd: List[str] = field(default_factory=list)
    docker_usage: List[str] = field(default_factory=list)
    configuration_files: List[str] = field(default_factory=list)
    architecture_style: str = "Unspecified / Generic"
    risk_areas: List[str] = field(default_factory=list)
    improvement_opportunities: List[str] = field(default_factory=list)

    def generate_report(self) -> str:
        lines: List[str] = []
        lines.append("ENGINEERING REPORT")
        lines.append(f"Languages: {', '.join(self.languages) if self.languages else 'None detected'}")
        lines.append(f"Frameworks: {', '.join(self.frameworks) if self.frameworks else 'None detected'}")
        lines.append(f"Architecture: {self.architecture_style}")
        lines.append(f"Entry Points: {', '.join(self.entry_points) if self.entry_points else 'None detected'}")
        lines.append(f"Dependencies: {', '.join(self.external_dependencies[:15])}{'...' if len(self.external_dependencies) > 15 else '' if self.external_dependencies else 'None detected'}")
        lines.append(f"Risk Areas: {', '.join(self.risk_areas) if self.risk_areas else 'No severe risk areas identified'}")
        lines.append(f"Improvement Opportunities: {', '.join(self.improvement_opportunities) if self.improvement_opportunities else 'No immediate improvements required'}")
        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "root_path": self.root_path,
            "languages": self.languages,
            "frameworks": self.frameworks,
            "package_manager": self.package_manager,
            "build_system": self.build_system,
            "test_framework": self.test_framework,
            "entry_points": self.entry_points,
            "dependency_graph": self.dependency_graph,
            "external_dependencies": self.external_dependencies,
            "ci_cd": self.ci_cd,
            "docker_usage": self.docker_usage,
            "configuration_files": self.configuration_files,
            "architecture_style": self.architecture_style,
            "risk_areas": self.risk_areas,
            "improvement_opportunities": self.improvement_opportunities,
        }


class ProjectIntelligence:
    """
    Offline-first engine that inspects real repository structures, code syntax,
    dependency configurations, and architectural patterns without assuming.
    """
    IGNORE_DIRS: Set[str] = {
        ".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache",
        "dist", "build", ".mypy_cache", ".tox", "target",
    }

    def __init__(self, repo_path: str | Path):
        self.repo_path = Path(repo_path).resolve()
        if not self.repo_path.exists():
            raise FileNotFoundError(f"Repository path does not exist: {self.repo_path}")

    def analyze(self) -> RepositoryInfo:
        info = RepositoryInfo(root_path=str(self.repo_path))
        
        file_ext_counts: Dict[str, int] = {}
        all_files: List[Path] = []
        py_files: List[Path] = []
        js_files: List[Path] = []
        
        for root, dirs, files in os.walk(self.repo_path):
            dirs[:] = [d for d in dirs if d not in self.IGNORE_DIRS]
            for file in files:
                fpath = Path(root) / file
                rel_path = str(fpath.relative_to(self.repo_path))
                all_files.append(fpath)
                ext = fpath.suffix.lower()
                if ext:
                    file_ext_counts[ext] = file_ext_counts.get(ext, 0) + 1
                if ext in {".py"}:
                    py_files.append(fpath)
                elif ext in {".js", ".ts", ".jsx", ".tsx"}:
                    js_files.append(fpath)

        # 1. Detect Languages
        ext_to_lang = {
            ".py": "Python", ".js": "JavaScript", ".ts": "TypeScript",
            ".go": "Go", ".rs": "Rust", ".java": "Java", ".cpp": "C++",
            ".c": "C", ".html": "HTML", ".css": "CSS", ".sh": "Shell",
            ".ps1": "PowerShell", ".sql": "SQL", ".md": "Markdown",
        }
        langs = set()
        for ext, _ in sorted(file_ext_counts.items(), key=lambda x: x[1], reverse=True):
            if ext in ext_to_lang:
                langs.add(ext_to_lang[ext])
        info.languages = sorted(list(langs)) or ["Plaintext"]

        # 2. Detect Package Manager & Build System
        if (self.repo_path / "poetry.lock").exists() or self._has_pyproject_section("tool.poetry"):
            info.package_manager = "Poetry"
            info.build_system = "Poetry"
        elif (self.repo_path / "uv.lock").exists() or self._has_pyproject_section("tool.uv"):
            info.package_manager = "uv"
            info.build_system = "Hatchling / setuptools"
        elif (self.repo_path / "pyproject.toml").exists():
            info.package_manager = "Pip / pyproject.toml"
            info.build_system = "pyproject (setuptools/hatch)"
        elif (self.repo_path / "requirements.txt").exists():
            info.package_manager = "Pip"
            info.build_system = "Setuptools"
        elif (self.repo_path / "package-lock.json").exists():
            info.package_manager = "npm"
            info.build_system = "npm scripts / webpack"
        elif (self.repo_path / "yarn.lock").exists():
            info.package_manager = "Yarn"
            info.build_system = "Yarn"
        elif (self.repo_path / "Cargo.toml").exists():
            info.package_manager = "Cargo"
            info.build_system = "Cargo"
        elif (self.repo_path / "Makefile").exists():
            info.build_system = "Make"

        # 3. Detect Frameworks & External Dependencies & Dependency Graph
        frameworks: Set[str] = set()
        ext_deps: Set[str] = set()
        dep_graph: Dict[str, List[str]] = {}

        # Parse requirements.txt / pyproject.toml / package.json
        req_file = self.repo_path / "requirements.txt"
        if req_file.exists():
            try:
                for line in req_file.read_text(encoding="utf-8", errors="ignore").splitlines():
                    line = line.strip()
                    if line and not line.startswith("#"):
                        pkg_name = re.split(r"[><=~!\[]", line)[0].strip()
                        if pkg_name:
                            ext_deps.add(pkg_name)
            except Exception:
                pass

        pkg_json = self.repo_path / "package.json"
        if pkg_json.exists():
            try:
                data = json.loads(pkg_json.read_text(encoding="utf-8", errors="ignore"))
                for k in list(data.get("dependencies", {}).keys()) + list(data.get("devDependencies", {}).keys()):
                    ext_deps.add(k)
            except Exception:
                pass

        # Inspect AST of Python files for imports and test discovery
        test_detected = False
        known_frameworks = {
            "pytest": "pytest", "fastapi": "FastAPI", "flask": "Flask",
            "django": "Django", "streamlit": "Streamlit", "uvicorn": "Uvicorn",
            "torch": "PyTorch", "tensorflow": "TensorFlow", "pydantic": "Pydantic",
            "sqlmodel": "SQLModel", "sqlalchemy": "SQLAlchemy", "celery": "Celery",
            "next": "Next.js", "react": "React", "express": "Express.js",
        }

        for fpath in py_files:
            rel_name = str(fpath.relative_to(self.repo_path)).replace("\\", "/")
            if "tests/" in rel_name or "test_" in fpath.name:
                test_detected = True
            try:
                content = fpath.read_text(encoding="utf-8", errors="ignore")
                tree = ast.parse(content, filename=str(fpath))
                imports: List[str] = []
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            root_pkg = alias.name.split(".")[0]
                            imports.append(root_pkg)
                            if root_pkg in known_frameworks:
                                frameworks.add(known_frameworks[root_pkg])
                    elif isinstance(node, ast.ImportFrom) and node.module:
                        root_pkg = node.module.split(".")[0]
                        imports.append(node.module)
                        if root_pkg in known_frameworks:
                            frameworks.add(known_frameworks[root_pkg])
                if imports:
                    dep_graph[rel_name] = sorted(list(set(imports)))
            except Exception:
                continue

        for f in ext_deps:
            if f.lower() in known_frameworks:
                frameworks.add(known_frameworks[f.lower()])

        if test_detected or "pytest" in ext_deps or (self.repo_path / "tests").exists():
            info.test_framework = "pytest / unittest"
            frameworks.add("pytest")

        info.frameworks = sorted(list(frameworks))
        info.external_dependencies = sorted(list(ext_deps))
        info.dependency_graph = dep_graph

        # 4. Detect Entry Points & CI/CD & Docker & Config Files
        entry_points: Set[str] = set()
        ci_cd: Set[str] = set()
        docker_usage: Set[str] = set()
        configs: Set[str] = set()

        for fpath in all_files:
            rel_str = str(fpath.relative_to(self.repo_path)).replace("\\", "/")
            fname = fpath.name
            
            # Entry points
            if fname in {"__main__.py", "main.py", "app.py", "run.py", "index.js", "server.js", "main.go", "manage.py"}:
                entry_points.add(rel_str)
            elif fpath.suffix in {".sh", ".ps1"} and fname in {"bootstrap.sh", "bootstrap.ps1", "run.sh", "run.ps1", "install.sh", "install.ps1"}:
                entry_points.add(rel_str)

            # CI/CD
            if ".github/workflows/" in rel_str or fname in {".gitlab-ci.yml", "Jenkinsfile", "circle.yml", "azure-pipelines.yml"}:
                ci_cd.add(rel_str)
            elif fname in {"Makefile", "tox.ini", "justfile"}:
                ci_cd.add(f"Automation logic via {fname}")

            # Docker
            if fname in {"Dockerfile", "docker-compose.yml", "docker-compose.yaml"} or ".dockerignore" in fname:
                docker_usage.add(rel_str)

            # Configs
            if fpath.suffix in {".ini", ".toml", ".yaml", ".yml", ".json", ".cfg"} or fname.startswith(".env") or fname in {".editorconfig", ".gitattributes", ".gitignore"}:
                if "package-lock.json" not in fname and "yarn.lock" not in fname and "test_console" not in rel_str:
                    configs.add(rel_str)

        info.entry_points = sorted(list(entry_points))
        info.ci_cd = sorted(list(ci_cd))
        info.docker_usage = sorted(list(docker_usage))
        info.configuration_files = sorted(list(configs))

        # 5. Detect Architecture Style
        has_src = (self.repo_path / "src").exists()
        has_agents = any("agents" in d.replace("\\", "/") for d in dep_graph.keys()) or any("agents" in str(f) for f in py_files)
        has_db = any(".db" in f.name for f in all_files)
        has_api = "FastAPI" in info.frameworks or "Flask" in info.frameworks or any("api.py" in str(f) or "server" in str(f) for f in py_files)
        
        if has_agents and has_src:
            info.architecture_style = "Layered Modular Autonomous Agent Architecture"
        elif has_api and (self.repo_path / "ui").exists():
            info.architecture_style = "Client-Server Web Service Architecture"
        elif has_api:
            info.architecture_style = "REST API / Microservices Module"
        elif has_src and entry_points:
            info.architecture_style = "Modular CLI & Library Distribution Architecture"
        elif len(py_files) == 1 or len(all_files) <= 5:
            info.architecture_style = "Standalone Single-File Script / Micro-Module"
        else:
            info.architecture_style = "Modular Software Package"

        # 6. Assess Risk Areas & Improvement Opportunities
        risks: List[str] = []
        improving: List[str] = []

        # SQLite risk check
        sqlite_count = sum(1 for f in all_files if f.suffix == ".db" or "sqlite" in str(f).lower())
        if sqlite_count > 0:
            risks.append("Embedded SQLite database usage detected without enterprise replication or automated schema migration tracking")
            improving.append("Replace embedded SQLite database storage with scalable PostgreSQL or distributed database backend")

        # Dependency pinning check
        if not info.external_dependencies and not (self.repo_path / "poetry.lock").exists():
            risks.append("No automated lockfile or explicit dependency pinning enforced across all manifests")
            improving.append("Enforce explicit package dependency pinning and generation of reproducible lockfiles")

        # Docker check
        if not docker_usage:
            improving.append("Containerize runtime environments using multi-stage Docker builds for isolated production deployment")
        elif "docker-compose.yml" in str(docker_usage):
            improving.append("Optimize Docker multi-stage configuration and resilience scaling health checks")

        # CI check
        if not any(".github" in str(c) for c in ci_cd):
            risks.append("Missing dedicated GitHub Actions CI/CD workflows for automated pre-merge verification")
            improving.append("Implement automated GitHub Actions validation pipeline to run comprehensive unit test suites")

        # Test coverage check
        if not info.test_framework or info.test_framework == "None detected":
            risks.append("Absence of formal unit test framework setup creates high vulnerability to silent regression failures")
            improving.append("Establish automated test suite covering all entry points and critical domain modules")

        if not risks:
            risks.append("Minimal structural architectural risk detected in baseline review")
        if not improving:
            improving.append("Perform routine refactoring and automated performance profiling")

        info.risk_areas = risks
        info.improvement_opportunities = improving
        
        return info

    def _has_pyproject_section(self, section: str) -> bool:
        toml_path = self.repo_path / "pyproject.toml"
        if not toml_path.exists():
            return False
        try:
            content = toml_path.read_text(encoding="utf-8", errors="ignore")
            return f"[{section}]" in content
        except Exception:
            return False
