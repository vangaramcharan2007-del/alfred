import time
import logging
from enum import Enum
import functools

class CircuitState(Enum):
    CLOSED = 1
    OPEN = 2
    HALF_OPEN = 3

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 3, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.state = CircuitState.CLOSED
        self.failures = 0
        self.last_failure_time = 0

    def call(self, func, *args, **kwargs):
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
            else:
                logging.warning(f"Circuit OPEN. Rejecting call to {func.__name__}.")
                raise Exception("CircuitBreaker: Action blocked to prevent cascading failure.")
                
        try:
            result = func(*args, **kwargs)
            
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
                self.failures = 0
                logging.info(f"Circuit CLOSED. {func.__name__} recovered.")
                
            return result
            
        except Exception as e:
            self.failures += 1
            self.last_failure_time = time.time()
            
            if self.failures >= self.failure_threshold:
                self.state = CircuitState.OPEN
                logging.error(f"Circuit OPENED for {func.__name__} after {self.failures} failures.")
                
            raise e

def circuit_protected(failure_threshold=3, recovery_timeout=60):
    breaker = CircuitBreaker(failure_threshold, recovery_timeout)
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return breaker.call(func, *args, **kwargs)
        return wrapper
    return decorator
