import pytest
from jarvisx.memory.providers.cognee_provider import CogneeProvider


@pytest.mark.asyncio
async def test_cognee_provider_save_and_search():
    provider = CogneeProvider()
    await provider.save("k1", {"type": "semantic", "fact": "User prefers cinematic editing"})
    results = await provider.search("cinematic")
    assert len(results) == 1
    assert results[0]["data"]["fact"] == "User prefers cinematic editing"


@pytest.mark.asyncio
async def test_cognee_provider_delete():
    provider = CogneeProvider()
    await provider.save("k1", {"fact": "test"})
    assert await provider.delete("k1") is True
    assert await provider.delete("k1") is False
    results = await provider.search("test")
    assert len(results) == 0


@pytest.mark.asyncio
async def test_cognee_provider_sync():
    provider = CogneeProvider()
    await provider.sync("node_a", {"k1": {"fact": "synced"}})
    results = await provider.search("synced")
    assert len(results) >= 1


def test_cognee_provider_graph_operations():
    provider = CogneeProvider()
    exp_id = provider.add_experience({"action": "video_edit", "result": "success"})
    assert exp_id.startswith("exp_")

    rel_id = provider.create_relationships("user", "cinematic_style", "prefers", 0.9)
    assert rel_id.startswith("rel_")

    ctx = provider.retrieve_context("user")
    assert len(ctx["relationships"]) == 1

    assert provider.sync_graph({"entities": {"e1": {"name": "test"}}, "relationships": []}) is True


def test_cognee_provider_search_knowledge():
    provider = CogneeProvider()
    provider._graph_entities["e1"] = {"name": "cinematic", "type": "preference"}
    results = provider.search_knowledge("cinematic")
    assert len(results) == 1
