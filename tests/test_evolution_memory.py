from jarvisx.evolution.evolution_memory import EvolutionMemory

def test_evolution_memory():
    mem = EvolutionMemory()
    rec = mem.record_evolution_event(
        upgrade_id="upg_001",
        reason="Low Java debugging rate",
        changes_made=["Added Java AST parser"],
        success=True,
        lessons_learned="Sandbox tests passed successfully"
    )

    assert rec.upgrade_id == "upg_001"
    history = mem.get_history()
    assert len(history) == 1
    assert history[0]["success"] is True
