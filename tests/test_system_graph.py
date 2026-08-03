from jarvisx.meta.system_graph import SystemKnowledgeGraph

def test_system_knowledge_graph():
    graph = SystemKnowledgeGraph()
    n1 = graph.add_node("cap_arch", "capability", "Architecture Agent")
    n2 = graph.add_node("prov_goose", "provider", "Goose Provider")

    edge = graph.add_edge("prov_goose", "cap_arch", "improves")

    assert len(graph.nodes) == 2
    assert len(graph.edges) == 1

    rels = graph.query_relationships("prov_goose")
    assert len(rels) == 1
    assert rels[0]["relation"] == "improves"
