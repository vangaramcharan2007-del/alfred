"""
asynchronous Token Bucket rate limiter utility for Jarvis X / Alfred OS.

This module provides a production-grade, asynchronous token bucket implementation
using only the Python standard library. It is designed to integrate with Jarvis X's
event-driven architecture, ensuring that external API calls (e.g., to Groq/Gemini)
are smoothed out to respect rate limits without blocking the main event loop.
"""

import asyncio
import time
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class TokenBucket:
    """
    An asynchronous Token Bucket rate limiter.
    
    Attributes:
        capacity: The maximum number of tokens the bucket can hold.
        refill_rate: The number of tokens added per second.
        tokens: The current number of available tokens.
        last_refill_time: The timestamp of the last token refill.
        lock: An asyncio lock to ensure thread-safety within the event loop.
    """
    capacity: float
    refill_rate: float  # tokens per second
    tokens: float = field(init=False)
    last_refill_time: float = field(init=False)
    lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False)

    def __post_init__(self):
        self.tokens = self.capacity
        self.last_refill_time = time.monotonic()
        # Ensure the lock is created in the context of the running loop if possible,
        # or lazily. In Python 3.10+, Lock() is safe to instantiate outside a loop,
        # but we ensure it's bound correctly.

    def _refill(self) -> None:
        """
        Refill tokens based on the time elapsed since the last refill.
        Must be called while holding the lock.
        """
        current_time = time.monotonic()
        time_diff = current_time - self.last_refill_time
        if time_diff <= 0:
            return
        
        # Calculate new tokens
        new_tokens = time_diff * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + new_tokens)
        self.last_refill_time = current_time

    async def acquire(self, tokens: float = 1.0) -> None:
        """
        Acquire tokens from the bucket. If insufficient tokens are available,
        waits until enough tokens have been refilled.
        
        Args:
            tokens: The number of tokens to acquire. Defaults to 1.0.
        
        Raises:
            ValueError: If the requested tokens exceed the bucket capacity.
        """
        if tokens > self.capacity:
            raise ValueError(
                f"Requested tokens {tokens} exceed bucket capacity {self.capacity}"
            )

        async with self.lock:
            # Loop until we have enough tokens
            while True:
                self._refill()
                
                if self.tokens >= tokens:
                    self.tokens -= tokens
                    return
                
                # Calculate how long to wait for enough tokens
                # We need (tokens - self.tokens) more tokens.
                # Time needed = deficit / refill_rate
                deficit = tokens - self.tokens
                wait_time = deficit / self.refill_rate
                
                # Yield control to the event loop
                await asyncio.sleep(wait_time)

    async def try_acquire(self, tokens: float = 1.0) -> bool:
        """
        Attempt to acquire tokens without waiting.
        
        Args:
            tokens: The number of tokens to acquire.
            
        Returns:
            True if tokens were acquired, False otherwise.
        """
        if tokens > self.capacity:
            return False

        async with self.lock:
            self._refill()
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False

    @property
    def available_tokens(self) -> float:
        """
        Get the current number of available tokens.
        Note: This does not hold the lock and may be slightly stale.
        For accurate metrics during high contention, use try_acquire logic.
        """
        # We don't lock here to allow non-blocking status checks,
        # but this is an approximation.
        self._refill()
        return self.tokens