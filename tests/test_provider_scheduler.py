import pytest
from jarvisx.providers.intelligence.provider_scheduler import ProviderScheduler

def test_provider_scheduler_priority_and_reservations():
    scheduler = ProviderScheduler()

    t1 = scheduler.submit_task("task_low", priority=10, action="doc", params={})
    t2 = scheduler.submit_task("task_high", priority=1, action="security", params={})

    next_task = scheduler.pop_next_task()
    assert next_task.task_id == "task_high"

    res = scheduler.reserve_provider("goose", "task_high")
    assert res is True
    assert scheduler.is_provider_available("goose") is False

    scheduler.release_provider("goose")
    assert scheduler.is_provider_available("goose") is True
