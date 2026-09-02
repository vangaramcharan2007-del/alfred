"""
Jarvis X / Alfred OS - Rate Limiter Module
High-throughput, non-blocking Token Bucket rate limiter with sliding window burst control.
Designed for Groq and Gemini API integration.
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class TokenBucketConfig:
    """Configuration for the Token Bucket."""
    max_tokens: float
    refill_rate: float  # Tokens per second
    burst_size: Optional[float] = None  # Max burst allowed (defaults to max_tokens)


class TokenBucketRateLimiter:
    """
    A non-blocking, async-safe Token Bucket rate limiter.
    
    This limiter uses a sliding window approach to refill tokens based on 
    elapsed time since the last update, ensuring precise burst control 
    without fixed-interval drift.
    """

    def __init__(self, config: TokenBucketConfig):
        self.config = config
        self._tokens: float = config.max_tokens
        self._last_refill_time: float = time.monotonic()
        self._lock = asyncio.Lock()
        # Burst control: If burst_size is not specified, allow full bucket burst
        self._max_burst = config.burst_size if config.burst_size is not None else config.max_tokens

    def _refill_tokens(self) -> None:
        """
        Calculate and apply token refill based on elapsed time.
        Must be called while holding the lock.
        """
        now = time.monotonic()
        elapsed_time = now - self._last_refill_time
        
        if elapsed_time > 0:
            tokens_to_add = elapsed_time * self.config.refill_rate
            # Cap tokens at max_tokens
            self._tokens = min(self.config.max_tokens, self._tokens + tokens_to_add)
            self._last_refill_time = now

    async def acquire(self, tokens: float = 1.0) -> bool:
        """
        Attempt to acquire tokens from the bucket.
        
        This method is non-blocking in the sense that it yields control 
        to the event loop if tokens are insufficient, allowing other tasks 
        to proceed. It does NOT block the thread.
        
        Args:
            tokens: Number of tokens to acquire.
            
        Returns:
            bool: True if tokens were acquired, False if rate limit is exceeded 
                  and no tokens are available.
        """
        async with self._lock:
            self._refill_tokens()
            
            if self._tokens >= tokens:
                self._tokens -= tokens
                return True
            
            # If we don't have enough tokens, we cannot acquire immediately.
            # In a high-throughput scenario, we might want to wait, but for 
            # strict non-blocking behavior in this implementation, we return False.
            # The caller (e.g., Jarvis Brain) should handle retry logic or queueing.
            return False

    async def wait_for_tokens(self, tokens: float = 1.0) -> None:
        """
        Wait until tokens are available, then acquire them.
        
        This is a non-blocking wait that sleeps in the event loop, 
        allowing other Jarvis components to run.
        
        Args:
            tokens: Number of tokens to acquire.
        """
        while True:
            async with self._lock:
                self._refill_tokens()
                
                if self._tokens >= tokens:
                    self._tokens -= tokens
                    return
                
                # Calculate how long to wait until enough tokens are available
                deficit = tokens - self._tokens
                wait_time = deficit / self.config.refill_rate
                # Ensure we don't wait longer than the time to refill the whole bucket (safety)
                wait_time = min(wait_time, self.config.max_tokens / self.config.refill_rate)
            
            # Release lock while sleeping to allow other tasks to check status
            await asyncio.sleep(wait_time)

    def get_status(self) -> dict:
        """Return current status of the rate limiter for monitoring."""
        # Note: This is not thread-safe for exact real-time values, 
        # but sufficient for logging/monitoring.
        return {
            "current_tokens": self._tokens,
            "max_tokens": self.config.max_tokens,
            "refill_rate": self.config.refill_rate,
            "last_refill_time": self._last_refill_time
        }


# Factory function for convenience in Jarvis Brain
def create_groq_limiter() -> TokenBucketRateLimiter:
    """Create a rate limiter optimized for Groq API (high throughput)."""
    return TokenBucketRateLimiter(TokenBucketConfig(max_tokens=50, refill_rate=25.0))

def create_gemini_limiter() -> TokenBucketRateLimiter:
    """Create a rate limiter optimized for Gemini API (moderate throughput)."""
    return TokenBucketRateLimiter(TokenBucketConfig(max_tokens=20, refill_rate=10.0))