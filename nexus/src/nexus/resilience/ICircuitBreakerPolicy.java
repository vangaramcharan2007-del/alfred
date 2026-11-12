package nexus.resilience;

import java.util.function.Supplier;

/**
 * Enterprise contract for Circuit Breaker State Machine & Fault-Tolerant Fallbacks.
 */
public interface ICircuitBreakerPolicy {
    String getName();
    CircuitBreaker.State getState();
    <T> T execute(Supplier<T> operation, Supplier<T> fallback);
    void recordSuccess();
    void recordFailure();
    void reset();
}
