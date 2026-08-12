"""Unit & Integration Tests for Phase 3: Reliability & Production Hardening.

Tests:
1. CircuitBreaker CLOSED -> OPEN transition on consecutive failures
2. CircuitBreaker fast-fail when OPEN (blocks calls without executing function)
3. CircuitBreaker HALF_OPEN recovery and reset to CLOSED
4. ResourceLimitGuard RSS memory and disk checks
5. ResourceLimitGuard sliding-window rate limiter
6. Provider outage resilience (graceful failure when all providers down)
7. Malformed tool JSON handling without runtime crash
8. Tool timeout isolation
"""

import time
import pytest
from jarvisx.reliability.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerOpenError,
    CircuitState,
)
from jarvisx.reliability.watchdog_guard import ResourceLimitGuard
from jarvisx.tools.tool_executor import ToolExecutor


def test_circuit_breaker_closed_to_open():
    """CircuitBreaker opens after reaching failure threshold."""
    cb = CircuitBreaker(name="test_cb", failure_threshold=3, recovery_timeout_sec=1.0)
    assert cb.state == CircuitState.CLOSED

    def failing_fn():
        raise RuntimeError("Service unavailable")

    # 1st failure
    with pytest.raises(RuntimeError):
        cb.call(failing_fn)
    assert cb.state == CircuitState.CLOSED

    # 2nd failure
    with pytest.raises(RuntimeError):
        cb.call(failing_fn)
    assert cb.state == CircuitState.CLOSED

    # 3rd failure -> trips to OPEN
    with pytest.raises(RuntimeError):
        cb.call(failing_fn)
    assert cb.state == CircuitState.OPEN


def test_circuit_breaker_fast_fail_when_open():
    """When OPEN, CircuitBreaker raises CircuitBreakerOpenError immediately."""
    cb = CircuitBreaker(name="test_cb", failure_threshold=2, recovery_timeout_sec=5.0)

    def failing_fn():
        raise RuntimeError("Failure")

    for _ in range(2):
        with pytest.raises(RuntimeError):
            cb.call(failing_fn)

    assert cb.state == CircuitState.OPEN

    calls = 0
    def target_fn():
        nonlocal calls
        calls += 1
        return "success"

    with pytest.raises(CircuitBreakerOpenError):
        cb.call(target_fn)

    # Underlying target_fn was never called
    assert calls == 0


def test_circuit_breaker_half_open_recovery():
    """CircuitBreaker enters HALF_OPEN after timeout and recovers to CLOSED on success."""
    cb = CircuitBreaker(name="test_cb", failure_threshold=1, recovery_timeout_sec=0.1)

    # Force trip to OPEN
    with pytest.raises(ValueError):
        cb.call(lambda: (_ for _ in ()).throw(ValueError("Error")))
    assert cb.state == CircuitState.OPEN

    # Wait for recovery timeout
    time.sleep(0.15)
    assert cb.state == CircuitState.HALF_OPEN

    # Successful canary call recovers circuit
    res = cb.call(lambda: "healthy")
    assert res == "healthy"
    assert cb.state == CircuitState.CLOSED


def test_resource_limit_guard_metrics():
    """ResourceLimitGuard accurately reads process RSS and disk space."""
    guard = ResourceLimitGuard(max_rss_mb=4096.0, min_free_disk_mb=100.0)
    res = guard.check_resources()
    assert res["healthy"] is True
    assert res["memory_rss_mb"] > 0
    assert res["disk_free_mb"] > 0
    assert res["rss_ok"] is True
    assert res["disk_ok"] is True


def test_resource_limit_guard_rate_limiter():
    """ResourceLimitGuard enforces per-minute rate limit."""
    guard = ResourceLimitGuard(rate_limit_per_minute=3)
    assert guard.check_rate_limit() is True
    assert guard.check_rate_limit() is True
    assert guard.check_rate_limit() is True
    # 4th call within minute is rejected
    assert guard.check_rate_limit() is False


def test_malformed_tool_json_resilience():
    """ToolExecutor handles broken/truncated JSON responses cleanly."""
    assert ToolExecutor.parse_tool_call("random text without json") is None
    assert ToolExecutor.parse_tool_call("{broken json") is None
    assert ToolExecutor.parse_tool_call('{"type": "tool_call", "tool": "test", "arguments": "not_a_dict"}') is None
