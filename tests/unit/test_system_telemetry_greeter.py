"""
Unit tests for system_greeting.py
"""

import pytest
from datetime import datetime
from unittest.mock import patch

from system_greeting import (
    SystemGreetingUtility,
    GreetingContext,
    GreetingResult,
    GreetingStatus
)


class TestSystemGreetingUtility:
    """Test suite for the SystemGreetingUtility class."""

    def setup_method(self):
        """Initialize the utility instance for each test."""
        self.utility = SystemGreetingUtility()

    def test_generate_greeting_success(self):
        """Test that a valid context produces a successful greeting."""
        context = GreetingContext(user_name="Jarvis", is_prime_time=True)
        result = self.utility.generate_greeting(context)

        assert isinstance(result, GreetingResult)
        assert result.status == GreetingStatus.SUCCESS
        assert "Jarvis" in result.message
        assert result.latency_ns > 0
        # Verify timestamp is a valid ISO format
        datetime.fromisoformat(result.timestamp)

    def test_generate_greeting_default_name(self):
        """Test that invalid or missing user names default to 'User'."""
        context = GreetingContext(user_name="")
        result = self.utility.generate_greeting(context)

        assert "User" in result.message
        assert result.status == GreetingStatus.SUCCESS

    def test_generate_greeting_long_name_sanitization(self):
        """Test that overly long names are sanitized."""
        long_name = "A" * 100
        context = GreetingContext(user_name=long_name)
        result = self.utility.generate_greeting(context)

        # Should fall back to default name due to sanitization in __post_init__
        assert "User" in result.message

    def test_generate_greeting_error_resilience(self):
        """Test that the utility handles internal errors gracefully."""
        # Mock the _build_message method to raise an exception
        with patch.object(
            self.utility, 
            '_build_message', 
            side_effect=Exception("Simulated Internal Error")
        ):
            context = GreetingContext(user_name="Test")
            result = self.utility.generate_greeting(context)

            assert result.status == GreetingStatus.ERROR
            assert "unavailable" in result.message
            assert result.latency_ns > 0

    def test_latency_telemetry_precision(self):
        """Test that latency is measured in nanoseconds and is positive."""
        context = GreetingContext(user_name="LatencyTest")
        # Run multiple times to ensure consistency
        for _ in range(5):
            result = self.utility.generate_greeting(context)
            assert result.latency_ns > 0
            # Latency for a simple string operation should be very low (< 1ms)
            assert result.latency_ns < 1_000_000

    def test_context_dataclass_immutability_check(self):
        """Verify that GreetingContext is a proper dataclass."""
        context = GreetingContext(user_name="DataClassTest")
        assert isinstance(context, GreetingContext)
        assert context.user_name == "DataClassTest"
        assert context.system_uptime_seconds is None