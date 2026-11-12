package nexus.vault;

import nexus.common.exceptions.VaultSecurityException;

/**
 * Enterprise contract for AES-256 Encrypted Backups and Rolling Hash Ledger Auditing.
 */
public interface IEncryptedVault {
    String createEncryptedSnapshot(String payload) throws VaultSecurityException;
    String restoreEncryptedSnapshot(String encryptedHex) throws VaultSecurityException;
    boolean verifyRollingLedgerIntegrity();
    int getChainLength();
    String getHeadHash();
}
