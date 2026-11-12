package nexus.common.exceptions;

import java.time.Instant;

/**
 * Base unchecked runtime exception for NEXUS.
 */
public class NexusRuntimeException extends RuntimeException {
    private final String errorCode;
    private final Instant timestamp;

    public NexusRuntimeException(String errorCode, String message) {
        super(String.format("[%s] %s", errorCode, message));
        this.errorCode = errorCode;
        this.timestamp = Instant.now();
    }

    public NexusRuntimeException(String errorCode, String message, Throwable cause) {
        super(String.format("[%s] %s", errorCode, message), cause);
        this.errorCode = errorCode;
        this.timestamp = Instant.now();
    }

    public String getErrorCode() {
        return errorCode;
    }

    public Instant getTimestamp() {
        return timestamp;
    }
}
