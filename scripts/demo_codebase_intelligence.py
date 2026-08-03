#!/usr/bin/env python3
"""
Live Demonstration Script for Phase 29: Codebase Intelligence + Long-Term Engineering Memory
Demonstrates repository profiling, knowledge graph building, dependency impact analysis,
change risk scoring, and architectural memory query.
"""

import asyncio
import json
import tempfile
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from jarvisx.capabilities.coding.pipeline.repository_analyzer import RepositoryAnalyzer
from jarvisx.capabilities.coding.code_graph import CodeGraph
from jarvisx.capabilities.coding.dependency_analyzer import DependencyAnalyzer
from jarvisx.capabilities.coding.change_risk import ChangeRiskAnalyzer
from jarvisx.capabilities.coding.architecture_memory import ArchitectureMemory
from jarvisx.capabilities.coding.pipeline.code_executor import FileChangeRecord

async def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    print("=" * 80)
    print("   JARVIS X - PHASE 29 CODEBASE INTELLIGENCE & ENGINEERING MEMORY DEMO")
    print("=" * 80)

    with tempfile.TemporaryDirectory() as repo_dir:
        repo_path = Path(repo_dir)
        print(f"\n📂 Step 1: Initializing Sample Multi-Module Repository at {repo_path}")

        # Create multi-file FastAPI + Auth + Database architecture
        (repo_path / "database.py").write_text("class Database:\n    def connect(self): pass\n", encoding="utf-8")
        (repo_path / "auth.py").write_text("import database\nfrom database import Database\n\nclass AuthService:\n    def authenticate(self, user, key):\n        pass\n", encoding="utf-8")
        (repo_path / "main.py").write_text("from fastapi import FastAPI\nimport auth\nfrom auth import AuthService\n\napp = FastAPI(title='JarvisX Enterprise')\n@app.post('/login')\ndef login(): pass\n", encoding="utf-8")
        (repo_path / "test_auth.py").write_text("import auth\ndef test_login(): assert True\n", encoding="utf-8")

        # Step 2: Repository Profiler
        print("\n🔍 Step 2: Running Repository Profiler...")
        analyzer = RepositoryAnalyzer()
        profile = analyzer.generate_profile(str(repo_path))
        print(f"   Primary Language:   {profile.language.upper()}")
        print(f"   Framework:          {profile.framework}")
        print(f"   Architecture Style: {profile.architecture_style}")
        print(f"   Entry Points:       {profile.entry_points}")
        print(f"   Important Files:    {profile.important_files}")

        # Step 3: Knowledge Graph Construction
        print("\n🕸️  Step 3: Building Codebase Knowledge Graph...")
        graph = CodeGraph()
        graph.build_from_repository(str(repo_path))
        graph_dict = graph.to_dict()
        print(f"   Nodes Identified:         {graph_dict['total_nodes']}")
        print(f"   Relationships Extracted:  {graph_dict['total_relationships']}")
        for n in graph.nodes.values():
            deps = [d.name for d in graph.get_dependencies(n.id)]
            print(f"   - Node [{n.node_type.upper()}] '{n.name}' -> Depends on: {deps}")

        # Step 4: Dependency Impact Analysis
        print("\n⚡ Step 4: Dependency Impact Analysis for Target File 'auth.py'...")
        dep_analyzer = DependencyAnalyzer(code_graph=graph)
        impact = dep_analyzer.analyze_impact(["auth.py"])
        print(f"   Affected Files:    {impact.affected_files}")
        print(f"   Affected Modules:  {impact.affected_modules}")
        print(f"   Calculated Risk:   {impact.risk_level}")
        print(f"   Recommended Tests: {impact.recommended_tests}")

        # Step 5: Change Risk Assessment
        print("\n🛡️  Step 5: Assessing Change Risk for Proposed Edits...")
        risk_analyzer = ChangeRiskAnalyzer(dependency_analyzer=dep_analyzer)
        proposed_changes = [
            FileChangeRecord(
                file_path="auth.py",
                action="modified",
                content_after="import database\n# Core auth modification with hardcoded secret test api_key='sk-secret-123'\n"
            )
        ]
        risk_assess = risk_analyzer.calculate_risk(proposed_changes, impact_report=impact)
        print(f"   Risk Score:      {risk_assess.risk_score} / 1.0")
        print(f"   Risk Level:      {risk_assess.risk_level}")
        print(f"   Risk Factors:    {risk_assess.risk_factors}")
        print(f"   Recommendations: {risk_assess.recommendations}")

        # Step 6: Architecture Memory Storage & Retrieval
        print("\n🧠 Step 6: Querying & Persisting Architecture Memory...")
        arch_mem = ArchitectureMemory()
        await arch_mem.store_architecture_pattern(
            pattern_name="fastapi_jwt_auth_service",
            details={
                "framework": "FastAPI",
                "auth": "JWT",
                "database_module": "database.py",
                "security_rules": "Always validate JWT claims; zero hardcoded keys"
            }
        )
        context_res = await arch_mem.query_architecture_context("fastapi_jwt_auth_service")
        print(f"   Retrieved Architectural Context: {json.dumps(context_res, indent=2)}")

        print("\n✨ Phase 29 Codebase Intelligence & Engineering Memory Demonstration Complete!")
        print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())
