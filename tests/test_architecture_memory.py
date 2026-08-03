import pytest
from jarvisx.capabilities.coding.architecture_memory import ArchitectureMemory

@pytest.mark.asyncio
async def test_architecture_memory_store_and_query():
    arch_mem = ArchitectureMemory()
    res = await arch_mem.store_architecture_pattern(
        pattern_name="fastapi_jwt_auth",
        details={"framework": "FastAPI", "auth": "JWT", "user_model": "SQLAlchemy User"}
    )
    assert res is not None

    query_res = await arch_mem.query_architecture_context("fastapi_jwt_auth")
    assert len(query_res) >= 1
    assert query_res[0]["pattern_name"] == "fastapi_jwt_auth"
