import pytest
import tempfile
from pathlib import Path
from jarvisx.capabilities.coding.code_graph import CodeGraph, Node, Relationship
from jarvisx.capabilities.coding.dependency_analyzer import DependencyAnalyzer

def test_dependency_analyzer_impact():
    graph = CodeGraph()
    graph.add_node(Node(id="file:auth.py", name="auth.py", node_type="file", path="auth.py"))
    graph.add_node(Node(id="file:main.py", name="main.py", node_type="file", path="main.py"))
    graph.add_node(Node(id="file:test_auth.py", name="test_auth.py", node_type="file", path="test_auth.py"))

    graph.add_relationship(Relationship(source_id="file:main.py", target_id="file:auth.py", rel_type="imports"))
    graph.add_relationship(Relationship(source_id="file:test_auth.py", target_id="file:auth.py", rel_type="imports"))

    analyzer = DependencyAnalyzer(code_graph=graph)
    report = analyzer.analyze_impact(["auth.py"])

    assert "main.py" in report.affected_files
    assert "test_auth.py" in report.affected_files
    assert report.risk_level in ["MEDIUM", "HIGH"]
    assert len(report.recommended_tests) >= 1
