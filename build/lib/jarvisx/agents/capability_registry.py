"""Self-Describing Capability Registry for Phase 91 Autonomous Mission Brain."""

from __future__ import annotations
import math
import os
import shutil
import subprocess
import webbrowser
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from jarvisx.agents.action_models import Capability, RiskLevel


class AutonomousCapabilityRegistry:
    """Self-describing capability registry for dynamic tool discovery by LLM planner."""

    def __init__(self):
        self.capabilities: Dict[str, Capability] = {}
        self._register_default_production_capabilities()

    def register(self, cap: Capability) -> None:
        """Register a new self-describing capability."""
        self.capabilities[cap.name] = cap

    def get(self, name: str) -> Optional[Capability]:
        """Get capability by canonical name."""
        return self.capabilities.get(name)

    def list_all(self) -> List[Capability]:
        """Return all registered capabilities."""
        return list(self.capabilities.values())

    def discover_for_goal(self, goal: str, top_k: int = 5) -> List[Capability]:
        """Semantic/keyword relevance matching to discover matching capabilities for any goal."""
        words = set(goal.lower().replace(",", " ").replace(".", " ").split())
        scored: List[tuple[float, Capability]] = []

        for cap in self.capabilities.values():
            if not cap.enabled:
                continue

            desc_words = set(cap.description.lower().split())
            name_words = set(cap.name.lower().split("_"))
            cat_words = set(cap.category.lower().split())

            # Overlap scoring
            overlap = len(words.intersection(desc_words | name_words | cat_words))
            # Base category boost
            score = float(overlap)
            if cap.category in words:
                score += 2.0

            scored.append((score, cap))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored[:top_k]]

    def _register_default_production_capabilities(self):
        """Register core system capabilities with exact risk levels and permissions."""

        # 1. Project & File Generator
        def handle_file_generator(target_path: str, content: str, **kwargs) -> Dict[str, Any]:
            p = Path(target_path)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
            return {"status": "SUCCESS", "created_file": str(p), "size_bytes": len(content)}

        self.register(Capability(
            name="file_generator",
            description="Create or generate source code, tests, markdown notes, configurations, or documents on disk",
            category="filesystem",
            inputs=["target_path", "content"],
            risk_level=RiskLevel.LOW,
            permissions=["filesystem_write"],
            handler=handle_file_generator
        ))

        # 2. Document & Notes Synthesizer
        def handle_doc_generator(output_dir: str, title: str, sections: Dict[str, str], **kwargs) -> Dict[str, Any]:
            out_p = Path(output_dir) / f"{title.lower().replace(' ', '_')}.md"
            out_p.parent.mkdir(parents=True, exist_ok=True)
            lines = [f"# {title}\n"]
            for heading, body in sections.items():
                lines.append(f"## {heading}\n{body}\n")
            out_p.write_text("\n".join(lines), encoding="utf-8")
            return {"status": "SUCCESS", "document": str(out_p), "section_count": len(sections)}

        self.register(Capability(
            name="document_generator",
            description="Synthesize structured markdown study notes, summaries, architecture guides, and revision sheets",
            category="synthesis",
            inputs=["output_dir", "title", "sections"],
            risk_level=RiskLevel.LOW,
            permissions=["filesystem_write"],
            handler=handle_doc_generator
        ))

        # 3. Interactive Quiz & Assessment Generator
        def handle_quiz_generator(output_dir: str, topic: str, questions: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
            import json
            out_p = Path(output_dir) / f"{topic.lower().replace(' ', '_')}_quiz.json"
            out_p.parent.mkdir(parents=True, exist_ok=True)
            out_p.write_text(json.dumps({"topic": topic, "questions": questions}, indent=2), encoding="utf-8")
            return {"status": "SUCCESS", "quiz_file": str(out_p), "question_count": len(questions)}

        self.register(Capability(
            name="quiz_generator",
            description="Generate structured self-testing quizzes and assessment questions with solutions for exam prep",
            category="education",
            inputs=["output_dir", "topic", "questions"],
            risk_level=RiskLevel.LOW,
            permissions=["filesystem_write"],
            handler=handle_quiz_generator
        ))

        # 4. Folder Organizer
        def handle_folder_organizer(folder_path: str, **kwargs) -> Dict[str, Any]:
            from jarvisx.automation.desktop_actions import organize_folder
            return organize_folder(folder_path)

        self.register(Capability(
            name="folder_organizer",
            description="Organize, sort, and categorize documents, papers, downloads, and files by type and topic",
            category="organization",
            inputs=["folder_path"],
            risk_level=RiskLevel.MEDIUM,
            permissions=["filesystem_write", "filesystem_move"],
            handler=handle_folder_organizer
        ))

        # 5. System Cleaner
        def handle_system_cleaner(target_root: str = ".", **kwargs) -> Dict[str, Any]:
            from jarvisx.automation.real_system_cleaner import RealSystemCleaner
            cleaner = RealSystemCleaner()
            return cleaner.scan_and_clean_temp_bloat(target_root, delete=True)

        self.register(Capability(
            name="system_cleaner",
            description="Scan and purge temporary bytecode cache files, logs, and reclaim wasted hard disk storage",
            category="maintenance",
            inputs=["target_root"],
            risk_level=RiskLevel.MEDIUM,
            permissions=["filesystem_delete"],
            handler=handle_system_cleaner
        ))

        # 6. Web & Browser Search
        def handle_browser_search(query: str, **kwargs) -> Dict[str, Any]:
            url = f"https://www.google.com/search?q={query}"
            webbrowser.open(url)
            return {"status": "SUCCESS", "searched_query": query, "url": url}

        self.register(Capability(
            name="browser_search",
            description="Search the web for documentation, syllabus, videos, articles, and research sources",
            category="research",
            inputs=["query"],
            risk_level=RiskLevel.LOW,
            permissions=["network_access", "browser_launch"],
            handler=handle_browser_search
        ))

        # 7. Package Installer
        def handle_package_installer(package_name: str, **kwargs) -> Dict[str, Any]:
            from jarvisx.automation.super_stark_automation import SuperStarkAutomation
            stark = SuperStarkAutomation()
            return stark.download_and_install_app(package_name)

        self.register(Capability(
            name="package_installer",
            description="Download and install Windows applications or Python packages via winget or pip",
            category="installation",
            inputs=["package_name"],
            risk_level=RiskLevel.HIGH,
            permissions=["admin_install", "network_access"],
            handler=handle_package_installer
        ))
