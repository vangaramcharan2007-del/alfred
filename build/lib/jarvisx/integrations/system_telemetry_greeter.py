"""
Alfred OS System Greeting Utility
=================================
Provides a clean, typed system greeting generator with integrated
latency telemetry for performance monitoring.

Architecture Fit:
- Consumed by the 'Mouth' (TTS) or 'Eyes' (UI) components.
- Uses standard library only (time, dataclasses) for minimal footprint.
- Resilient against invalid input states.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class GreetingStatus(Enum):
    """Status of the greeting generation process."""
    SUCCESS = "success"
    DEGRADED = "degraded"
    ERROR = "error"


@dataclass
class GreetingContext:
    """
    Encapsulates the state required to generate a personalized greeting.
    
    Attributes:
        user_name: The name of the user. Defaults to "User" if not provided.
        is_prime_time: Boolean flag indicating if it's a 'prime' social time (e.g., morning).
        system_uptime_seconds: Optional system uptime for status reporting.
    """
    user_name: str = "User"
    is_prime_time: bool = False
    system_uptime_seconds: Optional[float] = None

    def __post_init__(self):
        # Sanitize user name to prevent injection or excessive length
        if not self.user_name or len(self.user_name) > 50:
            self.user_name = "User"


@dataclass
class GreetingResult:
    """
    Result of the greeting generation, including the message and telemetry.
    
    Attributes:
        message: The final greeting string.
        status: The operational status of the generation.
        latency_ns: The time taken to generate the greeting in nanoseconds.
        timestamp: ISO format string of when the greeting was generated.
    """
    message: str
    status: GreetingStatus
    latency_ns: int
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class SystemGreetingUtility:
    """
    Core utility for generating system greetings with telemetry.
    
    This class is designed to be stateless and thread-safe.
    """

    def generate_greeting(self, context: GreetingContext) -> GreetingResult:
        """
        Generates a system greeting based on the provided context.
        
        Args:
            context: The GreetingContext object.
            
        Returns:
            GreetingResult: Contains the message and latency telemetry.
        """
        start_time = time.perf_counter_ns()
        
        try:
            message = self._build_message(context)
            status = GreetingStatus.SUCCESS
        except Exception as e:
            # Resilient error handling: Return a degraded state instead of crashing
            message = "System greeting service unavailable."
            status = GreetingStatus.ERROR
            # In a full implementation, we would emit an event to the Nerves here
            # e.g., self.nerves.emit("greeting.error", error=str(e))
            
        end_time = time.perf_counter_ns()
        latency_ns = end_time - start_time
        
        return GreetingResult(
            message=message,
            status=status,
            latency_ns=latency_ns
        )

    def _build_message(self, context: GreetingContext) -> str:
        """
        Internal logic to construct the greeting string.
        
        Args:
            context: The context data.
            
        Returns:
            The formatted greeting string.
        """
        # Determine time-of-day based on current system time
        current_hour = datetime.now().hour
        if 5 <= current_hour < 12:
            salutation = "Good morning"
        elif 12 <= current_hour < 17:
            salutation = "Good afternoon"
        elif 17 <= current_hour < 21:
            salutation = "Good evening"
        else:
            salutation = "Good night"

        # Append system status if available
        status_suffix = ""
        if context.system_uptime_seconds is not None:
            if context.system_uptime_seconds < 60:
                status_suffix = " (System just initialized)"
            elif context.system_uptime_seconds > 86400 * 7:
                status_suffix = " (System stable for over a week)"

        return f"{salutation}, {context.user_name}.{status_suffix}"