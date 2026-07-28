import pytest
from jarvisx.learning.knowledge_graph import KnowledgeGraph


def test_add_entity():
    graph = KnowledgeGraph()
    eid = graph.add_entity("user", "user")
    assert eid.startswith("ent_")
    entity = graph.get_entity("user")
    assert entity is not None
    assert entity["name"] == "user"
    assert entity["type"] == "user"


def test_entity_deduplication():
    graph = KnowledgeGraph()
    eid1 = graph.add_entity("user", "user")
    eid2 = graph.add_entity("user", "user")
    assert eid1 == eid2


def test_add_relationship():
    graph = KnowledgeGraph()
    graph.add_entity("user", "user")
    graph.add_entity("cinematic style", "preference")
    rel_id = graph.add_relationship("user", "cinematic style", "prefers", 0.9)
    assert rel_id.startswith("rel_")


def test_relationship_deduplication():
    graph = KnowledgeGraph()
    rel1 = graph.add_relationship("user", "cinematic", "prefers", 0.8)
    rel2 = graph.add_relationship("user", "cinematic", "prefers", 0.95)
    assert rel1 == rel2  # Same relationship, confidence updated


def test_query_relationships():
    graph = KnowledgeGraph()
    graph.add_relationship("user", "cinematic", "prefers", 0.9)
    graph.add_relationship("user", "slow pacing", "prefers", 0.85)
    graph.add_relationship("editing_agent", "video_editing", "performed", 1.0)

    rels = graph.query_relationships("user")
    assert len(rels) == 2

    rels2 = graph.query_relationships("editing_agent")
    assert len(rels2) == 1


def test_find_related():
    graph = KnowledgeGraph()
    graph.add_relationship("user", "cinematic", "prefers")
    graph.add_relationship("user", "slow pacing", "prefers")
    graph.add_relationship("user", "editing_agent", "uses")

    prefs = graph.find_related("user", relation_type="prefers")
    assert "cinematic" in prefs
    assert "slow pacing" in prefs
    assert "editing_agent" not in prefs

    all_related = graph.find_related("user")
    assert len(all_related) == 3


def test_to_dict():
    graph = KnowledgeGraph()
    graph.add_entity("user", "user")
    graph.add_relationship("user", "cinematic", "prefers")
    d = graph.to_dict()
    assert d["entity_count"] == 1
    assert d["relationship_count"] == 1
