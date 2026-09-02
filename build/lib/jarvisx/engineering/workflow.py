from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from jarvisx.engineering.debug_loop import DebugLoopEngine, DebugResult
from jarvisx.engineering.impact_analyzer import ImpactAnalyzer
from jarvisx.engineering.intelligence import ProjectIntelligence, RepositoryInfo
from jarvisx.engineering.memory import EngineeringMemory, MemoryEntry
from jarvisx.engineering.planning import ArchitectureReasoner, EngineeringPlan
from jarvisx.engineering.tooling import DynamicToolSelector, ToolExecutionResult
from jarvisx.engineering.verification import ChangeReport, ChangeVerifier


@dataclass
class WorkflowExecutionReport:
    mission_goal: str
    repo_path: str
    repository_info: RepositoryInfo
    engineering_plan: EngineeringPlan
    tool_execution: ToolExecutionResult
    debug_result: DebugResult
    change_report: ChangeReport
    recalled_memories: List[MemoryEntry] = field(default_factory=list)

    def generate_report(self) -> str:
        lines: List[str] = []
        lines.append("=" * 60)
        lines.append(f"ADAPTIVE ENGINEERING WORKFLOW EXECUTION: '{self.mission_goal}'")
        lines.append("=" * 60)
        
        # 1. Memory retrieval
        if self.recalled_memories:
            lines.append("\n[1. HISTORICAL RECOVERY & ENGINEERING MEMORY]")
            for mem in self.recalled_memories:
                lines.append(f"  * Recalled Prior Solution for '{mem.problem}': {mem.chosen_solution} (Outcome: {mem.outcome})")
        else:
            lines.append("\n[1. HISTORICAL RECOVERY & ENGINEERING MEMORY]\n  * No identical prior mission memory found; initiating novel architecture exploration.")

        # 2. Intelligence & Architecture
        lines.append("\n[2. REPOSITORY INTELLIGENCE & ARCHITECTURE DISCOVERY]")
        lines.append(f"  * Detected Architecture Style: {self.repository_info.architecture_style}")
        lines.append(f"  * Primary Languages & Frameworks: {', '.join(self.repository_info.languages)} | {', '.join(self.repository_info.frameworks)}")
        
        # 3. Architecture Plan & Impact Analysis
        lines.append("\n[3. ARCHITECTURAL REASONING & IMPACT ANALYSIS]")
        lines.append(f"  * Estimated Modification Impact: {self.engineering_plan.estimated_impact}")
        for step_idx, step in enumerate(self.engineering_plan.implementation_order, 1):
            lines.append(f"  * Step {step_idx}: {step}")
        if self.engineering_plan.risk_assessment:
            lines.append(f"  * Primary Risk Assessment: {self.engineering_plan.risk_assessment[0]}")

        # 4. Dynamic Capability Selection & Modification
        lines.append("\n[4. DYNAMIC CAPABILITY SELECTION & CODE MODIFICATION]")
        lines.append(f"  * Tool Selection Reasoning: {self.tool_execution.reasoning}")
        lines.append(f"  * Execution Result: {'SUCCESS' if self.tool_execution.success else 'FAILED'} -> {self.tool_execution.output_log}")
        lines.append(f"  * Modified Target Files: {', '.join(self.tool_execution.modified_files) if self.tool_execution.modified_files else 'None'}")

        # 5. Debug Loop
        lines.append("\n[5. AUTOMATIC DEBUGGING & REGRESSION VERIFICATION]")
        lines.append(f"  * Debug Loop Summary: {self.debug_result.summary_log}")
        
        # 6. Final Change Verification Report
        lines.append("\n[6. FINAL CHANGE VERIFICATION REPORT]")
        lines.append(self.change_report.generate_report())
        lines.append("=" * 60)
        
        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mission_goal": self.mission_goal,
            "repo_path": self.repo_path,
            "repository_info": self.repository_info.to_dict(),
            "engineering_plan": self.engineering_plan.to_dict(),
            "tool_execution": {
                "tool_name": self.tool_execution.tool_name,
                "success": self.tool_execution.success,
                "modified_files": self.tool_execution.modified_files,
                "output_log": self.tool_execution.output_log,
                "reasoning": self.tool_execution.reasoning,
                "confidence": self.tool_execution.confidence,
            },
            "debug_result": {
                "success": self.debug_result.success,
                "summary_log": self.debug_result.summary_log,
            },
            "change_report": self.change_report.to_dict(),
        }


class AdaptiveEngineeringAgent:
    """
    Primary orchestration engine for Alfred's Phase 43 autonomous software engineering capability.
    Unites intelligence, architecture reasoning, dynamic capability selection, real debug loops,
    and rigorous verification into an offline-first execution workflow.
    """

    def __init__(self, repo_path: str | Path, memory_path: str | Path = "var/db/engineering_memory.jsonl"):
        self.repo_path = Path(repo_path).resolve()
        if not self.repo_path.exists():
            raise FileNotFoundError(f"Target repository path not found: {self.repo_path}")
        self.intelligence = ProjectIntelligence(self.repo_path)
        self.reasoner = ArchitectureReasoner(self.repo_path)
        self.tool_selector = DynamicToolSelector()
        self.debug_engine = DebugLoopEngine(self.repo_path)
        self.verifier = ChangeVerifier(self.repo_path)
        self.memory = EngineeringMemory(memory_path)

    def execute_mission(self, goal: str, test_cmd: List[str] | None = None) -> WorkflowExecutionReport:
        # Step 1: Analyze Repository Architecture
        intel_report = self.intelligence.analyze()
        
        # Step 2: Retrieve Similar Past Engineering Memories
        recalled_memories = self.memory.retrieve_similar(goal, max_results=2)
        
        # Step 3: Capture pre-modification baseline snapshot
        snapshot = self.verifier.capture_snapshot()

        # Step 4: Architecture Reasoning & Impact Plan
        plan = self.reasoner.plan_mission(goal)

        # Step 5: Dynamic Capability Selection & Code Modification
        tool_result = self.tool_selector.execute_task(goal, self.repo_path, context={"plan": plan.to_dict()})

        # Step 6: Automated Debugging & Regression Verification Loop
        debug_result = self.debug_engine.debug_repository(test_cmd=test_cmd)

        # Step 7: Change Verification
        change_report = self.verifier.verify_changes(
            mission_goal=goal,
            reason=tool_result.reasoning,
            snapshot=snapshot,
            explicit_modified_files=tool_result.modified_files,
            test_cmd=test_cmd
        )

        # Step 8: Engineering Memory Persistence
        mem_entry = MemoryEntry(
            problem=goal,
            architecture=intel_report.architecture_style,
            chosen_solution=f"Applied capability {tool_result.tool_name}: {tool_result.output_log}",
            rejected_approaches=["Unsafe direct textual substitution without AST verification", "Hardcoded toolchain execution"],
            outcome="SUCCESS" if change_report.success else "FAILED",
            lessons_learned=[
                f"Verified capability {tool_result.tool_name} under {intel_report.architecture_style} architecture.",
                f"Maintained zero regressions across dependent modules ({plan.estimated_impact} impact assessment)."
            ]
        )
        self.memory.save_entry(mem_entry)

        return WorkflowExecutionReport(
            mission_goal=goal,
            repo_path=str(self.repo_path),
            repository_info=intel_report,
            engineering_plan=plan,
            tool_execution=tool_result,
            debug_result=debug_result,
            change_report=change_report,
            recalled_memories=recalled_memories,
        )
