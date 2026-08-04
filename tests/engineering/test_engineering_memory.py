from __future__ import annotations

from pathlib import Path
from jarvisx.engineering.memory import EngineeringMemory, MemoryEntry


def test_engineering_memory_persistence_and_retrieval(tmp_path: Path) -> None:
    db_file = tmp_path / "eng_memory.jsonl"
    memory = EngineeringMemory(storage_path=db_file)
    memory.clear_memory()

    # 1. Create and persist historical entries
    entry1 = MemoryEntry(
        problem="Replace SQLite with PostgreSQL database server in high concurrency microservices",
        architecture="Layered Microservices Architecture",
        chosen_solution="Injected PostgresAdapter bridge into db_bridge.py with lazy connection initialization.",
        rejected_approaches=["Direct string search-and-replace across domain services"],
        outcome="SUCCESS",
        lessons_learned=["Abstracting the database adapter layer prevents downstream test breakage."]
    )
    memory.save_entry(entry1)

    entry2 = MemoryEntry(
        problem="Convert legacy Flask monolith to Docker multi-stage deployment container",
        architecture="Monolith Web Service",
        chosen_solution="Generated multi-stage Dockerfile isolating compilation build artifacts.",
        rejected_approaches=["Single stage bloated base container image"],
        outcome="SUCCESS",
        lessons_learned=["Multi-stage packaging reduces surface area vulnerability."]
    )
    memory.save_entry(entry2)

    # 2. Verify all entries are loaded cleanly from disk
    loaded = memory.get_all()
    assert len(loaded) == 2
    assert loaded[0].problem == entry1.problem
    assert loaded[0].chosen_solution == entry1.chosen_solution

    # 3. Test similarity-based retrieval for future missions
    recalled = memory.retrieve_similar("We need to replace our SQLite database storage with PostgreSQL")
    assert len(recalled) > 0
    assert recalled[0].problem == entry1.problem
    assert "PostgresAdapter" in recalled[0].chosen_solution
