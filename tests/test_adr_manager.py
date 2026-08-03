import pytest
from jarvisx.capabilities.coding.adr_manager import ADRManager

@pytest.mark.asyncio
async def test_adr_manager_creation_and_markdown():
    mgr = ADRManager()
    adr = await mgr.create_adr(
        title="Use PostgreSQL",
        context="Database storage selection",
        decision="Use PostgreSQL for primary store",
        consequences=["ACID compliance", "Relational querying"],
        alternatives=["MongoDB", "DynamoDB"]
    )

    assert adr.decision_id.startswith("ADR-")
    assert adr.status == "Accepted"
    assert mgr.get_adr(adr.decision_id) is not None

    md = mgr.format_as_markdown(adr)
    assert f"# {adr.decision_id}: Use PostgreSQL" in md
    assert "ACID compliance" in md
