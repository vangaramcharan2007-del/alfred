import pytest
import tempfile
from pathlib import Path
from jarvisx.capabilities.coding.code_graph import CodeGraph, Node, Relationship

def test_code_graph_nodes_and_relationships():
    graph = CodeGraph()
    n1 = Node(id="file:main.py", name="main.py", node_type="file", path="main.py")
    n2 = Node(id="file:auth.py", name="auth.py", node_type="file", path="auth.py")
    
    graph.add_node(n1)
    graph.add_node(n2)
    graph.add_relationship(Relationship(source_id="file:main.py", target_id="file:auth.py", rel_type="imports"))

    assert graph.get_node("file:main.py") is not None
    deps = graph.get_dependencies("file:main.py")
    assert len(deps) == 1
    assert deps[0].id == "file:auth.py"

    dependents = graph.get_dependents("file:auth.py")
    assert len(dependents) == 1
    assert dependents[0].id == "file:main.py"

def test_code_graph_repository_build():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        (root / "auth.py").write_text("class AuthController:\n    def login(self): pass\n", encoding="utf-8")
        (root / "main.py").write_text("import auth\nfrom auth import AuthController\n\ndef main(): pass\n", encoding="utf-8")

        graph = CodeGraph()
        graph.build_from_repository(tmpdir)

        assert len(graph.nodes) >= 2
        file_nodes = [n for n in graph.nodes.values() if n.node_type == "file"]
        assert len(file_nodes) == 2
        
        search_res = graph.search("auth")
        assert len(search_res) >= 1
