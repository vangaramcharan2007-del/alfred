package nexus.common.exceptions;

/**
 * Thrown when user credentials, session tokens, or zero-trust identity proofs fail validation.
 */
public class AuthenticationFailedException extends NexusException {
    private final String username;

    public AuthenticationFailedException(String username, String reason) {
        super(
            "ERR-AUTH-4003",
            "SECURITY_RBAC",
            String.format("Authentication failed for identity '%s': %s", username, reason)
        );
        this.username = username;
    }

    public String getUsername() {
        return username;
    }
}
