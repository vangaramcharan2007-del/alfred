package nexus.common.exceptions;

import java.time.Instant;

/**
 * Base checked exception for the NEXUS Enterprise Platform.
 * Encapsulates structured error codes, audit timestamps, and operational context.
 */
public class NexusException extends Exception {
    private final String errorCode;
    private final Instant timestamp;
    private final String subsystem;

    public NexusException(String errorCode, String subsystem, String message) {
        super(String.format("[%s][%s] %s", errorCode, subsystem, message));
        this.errorCode = errorCode;
        this.subsystem = subsystem;
        this.timestamp = Instant.now();
    }

    public NexusException(String errorCode, String subsystem, String message, Throwable cause) {
        super(String.format("[%s][%s] %s", errorCode, subsystem, message), cause);
        this.errorCode = errorCode;
        this.subsystem = subsystem;
        this.timestamp = Instant.now();
    }

    public String getErrorCode() {
        return errorCode;
    }

    public Instant getTimestamp() {
        return timestamp;
    }

    public String getSubsystem() {
        return subsystem;
    }
}
