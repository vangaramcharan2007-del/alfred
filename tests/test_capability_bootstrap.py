from __future__ import annotations

from jarvisx.capabilities.capability_loader import CapabilityLoader
from jarvisx.capabilities.capability_registry import CapabilityRegistry


EXPECTED_BUILT_INS = {"browser", "cad", "github"}


def test_built_in_capabilities_load() -> None:
    registry = CapabilityRegistry()
    loader = CapabilityLoader(registry)

    loader.load_built_in_sync()

    loaded = {adapter.manifest.name for adapter in registry.discover()}
    assert EXPECTED_BUILT_INS.issubset(loaded)


def test_runtime_starts_with_built_in_capabilities(tmp_path) -> None:
    from jarvisx.runtime import create_default_runtime

    runtime = create_default_runtime(
        op_db_path=tmp_path / "jarvisx_op.db",
        obsidian_vault=tmp_path / "vault",
        log_path=tmp_path / "jarvisx.jsonl",
    )
    try:
        loaded = {adapter.manifest.name for adapter in runtime.new_capability_registry.discover()}
        assert EXPECTED_BUILT_INS.issubset(loaded)
    finally:
        runtime.shutdown()
