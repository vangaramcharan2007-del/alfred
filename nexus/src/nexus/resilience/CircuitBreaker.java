package nexus.resilience;

import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;

/**
 * High-Concurrency Circuit Breaker State Machine (Closed -> Open -> Half-Open).
 * 
 * Author: Ram Charan Vanga (Reg No: RA2511027010164)
 * Department of Computer Science & Engineering
 * SRM Institute of Science and Technology, Kattankulathur
 */
public class CircuitBreaker implements ICircuitBreakerPolicy {
    public enum State {
        CLOSED,     // Normal operation - all calls pass through
        OPEN,       // Tripped - all calls fail fast or return cached fallback
        HALF_OPEN   // Testing recovery - limited probe calls allowed
    }

    private final String name;
    private final int failureThreshold;
    private final long recoveryTimeoutMs;

    private volatile State state = State.CLOSED;
    private final AtomicInteger failureCount = new AtomicInteger(0);
    private final AtomicInteger successCount = new AtomicInteger(0);
    private final AtomicLong lastStateChangeTime = new AtomicLong(System.currentTimeMillis());
    private final AtomicLong totalCalls = new AtomicLong(0);
    private final AtomicLong rejectedCalls = new AtomicLong(0);

    public CircuitBreaker(String name, int failureThreshold, long recoveryTimeoutMs) {
        this.name = name;
        this.failureThreshold = failureThreshold;
        this.recoveryTimeoutMs = recoveryTimeoutMs;
    }

    public boolean allowExecution() {
        totalCalls.incrementAndGet();
        long now = System.currentTimeMillis();

        if (state == State.OPEN) {
            if (now - lastStateChangeTime.get() >= recoveryTimeoutMs) {
                transitionTo(State.HALF_OPEN);
                return true;
            }
            rejectedCalls.incrementAndGet();
            return false;
        }

        return true;
    }

    public void recordSuccess() {
        failureCount.set(0);
        if (state == State.HALF_OPEN) {
            if (successCount.incrementAndGet() >= 2) {
                transitionTo(State.CLOSED);
            }
        }
    }

    public void recordFailure() {
        int failures = failureCount.incrementAndGet();
        if (state == State.CLOSED && failures >= failureThreshold) {
            transitionTo(State.OPEN);
        } else if (state == State.HALF_OPEN) {
            transitionTo(State.OPEN);
        }
    }

    public void tripManually() {
        transitionTo(State.OPEN);
    }

    public void reset() {
        failureCount.set(0);
        successCount.set(0);
        transitionTo(State.CLOSED);
    }

    private void transitionTo(State newState) {
        this.state = newState;
        this.lastStateChangeTime.set(System.currentTimeMillis());
        if (newState == State.CLOSED) {
            failureCount.set(0);
            successCount.set(0);
        }
    }

    public String getName() { return name; }
    public State getState() { return state; }
    public int getFailureCount() { return failureCount.get(); }
    public long getTotalCalls() { return totalCalls.get(); }
    public long getRejectedCalls() { return rejectedCalls.get(); }
    public long getRecoveryTimeoutMs() { return recoveryTimeoutMs; }
    public long getMsUntilHalfOpen() {
        if (state != State.OPEN) return 0;
        long elapsed = System.currentTimeMillis() - lastStateChangeTime.get();
        return Math.max(0, recoveryTimeoutMs - elapsed);
    }

    // --- ICircuitBreakerPolicy Implementation (Review 2 Rubric) ---
    @Override
    public <T> T execute(java.util.function.Supplier<T> operation, java.util.function.Supplier<T> fallback) {
        if (!allowExecution()) {
            return fallback != null ? fallback.get() : null;
        }
        try {
            T result = operation.get();
            recordSuccess();
            return result;
        } catch (Exception e) {
            recordFailure();
            return fallback != null ? fallback.get() : null;
        }
    }
}
