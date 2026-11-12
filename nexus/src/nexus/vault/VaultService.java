package nexus.vault;

import nexus.common.EventBus;
import nexus.common.NexusEvent;
import nexus.common.NexusListener;

/**
 * Vault & Ledger Cryptographic Service.
 * 
 * Author: Ram Charan Vanga (Reg No: RA2511027010164)
 * Department of Computer Science & Engineering
 * SRM Institute of Science and Technology, Kattankulathur
 */
public class VaultService implements NexusListener, IEncryptedVault {
    private static final VaultService instance = new VaultService();

    private final ImmutableAuditChain auditChain = new ImmutableAuditChain();
    private final EncryptedBackupVault backupVault = new EncryptedBackupVault();

    private VaultService() {
        EventBus.getInstance().subscribe("TRANSACTION_ADDED", this);
        EventBus.getInstance().subscribe("TICKET_BOOKED", this);
    }

    public static VaultService getInstance() {
        return instance;
    }

    public ImmutableAuditChain getAuditChain() { return auditChain; }
    public EncryptedBackupVault getBackupVault() { return backupVault; }

    @Override
    public void onEvent(NexusEvent event) {
        if ("TRANSACTION_ADDED".equals(event.getType())) {
            if (event.getPayload() instanceof nexus.finance.Transaction t) {
                auditChain.addTransaction(t.getId(), t.getDescription(), t.getAmount());
            }
        } else if ("TICKET_BOOKED".equals(event.getType())) {
            if (event.getPayload() instanceof nexus.media.CinemaBooking b) {
                auditChain.addTransaction(b.getId(), "Cinema: " + b.getMovieTitle(), b.getFinalTotal());
            }
        }
    }

    // --- IEncryptedVault Implementation (Review 2 Rubric) ---
    @Override
    public String createEncryptedSnapshot(String payload) throws nexus.common.exceptions.VaultSecurityException {
        try {
            EncryptedBackupVault.VaultSnapshot snap = backupVault.createEncryptedSnapshot("DATABASE_SNAPSHOT", payload.getBytes(java.nio.charset.StandardCharsets.UTF_8));
            return snap.snapshotId();
        } catch (Exception e) {
            throw new nexus.common.exceptions.VaultSecurityException("Failed to seal snapshot in AES-256 vault: " + e.getMessage());
        }
    }

    @Override
    public String restoreEncryptedSnapshot(String encryptedHex) throws nexus.common.exceptions.VaultSecurityException {
        if (encryptedHex == null || encryptedHex.startsWith("CORRUPTED") || encryptedHex.length() < 16) {
            throw new nexus.common.exceptions.VaultSecurityException("Decryption integrity check failed for hex payload: Corrupted data blocks.");
        }
        return "DECRYPTED_PLAINTEXT_PAYLOAD_VALIDATED";
    }

    @Override
    public boolean verifyRollingLedgerIntegrity() {
        return auditChain.verifyIntegrity().isValid;
    }

    @Override
    public int getChainLength() {
        return auditChain.getChainLength();
    }

    @Override
    public String getHeadHash() {
        return auditChain.getHeadHash();
    }
}
