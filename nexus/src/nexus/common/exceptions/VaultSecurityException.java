package nexus.common.exceptions;

/**
 * Thrown when AES-256 encrypted backups, HMAC signatures, or rolling SHA-256 audit chains
 * fail integrity validation or exhibit unauthorized tampering.
 */
public class VaultSecurityException extends NexusException {
    private final String expectedHash;
    private final String actualHash;

    public VaultSecurityException(String reason, String expectedHash, String actualHash) {
        super(
            "ERR-VAULT-5001",
            "CRYPTOGRAPHIC_VAULT",
            String.format("Cryptographic integrity violation: %s [Expected=%s, Actual=%s]", reason, expectedHash, actualHash)
        );
        this.expectedHash = expectedHash;
        this.actualHash = actualHash;
    }

    public VaultSecurityException(String reason) {
        super("ERR-VAULT-5002", "CRYPTOGRAPHIC_VAULT", reason);
        this.expectedHash = "N/A";
        this.actualHash = "N/A";
    }

    public String getExpectedHash() {
        return expectedHash;
    }

    public String getActualHash() {
        return actualHash;
    }
}
