package nexus.vault;

import javax.crypto.Cipher;
import javax.crypto.SecretKey;
import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.IvParameterSpec;
import javax.crypto.spec.PBEKeySpec;
import javax.crypto.spec.SecretKeySpec;
import java.nio.charset.StandardCharsets;
import java.security.SecureRandom;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

/**
 * Enterprise Database Backup Vault - AES-256-CBC Encryption & Point-In-Time Snapshots.
 * 
 * Author: Ram Charan Vanga (Reg No: RA2511027010164)
 * Department of Computer Science & Engineering
 * SRM Institute of Science and Technology, Kattankulathur
 */
public class EncryptedBackupVault {
    private static final String MASTER_PASSPHRASE = "NEXUS-V9-SRM-ACID-VAULT-2026";
    private static final int ITERATIONS = 65536;
    private static final int KEY_LENGTH = 256;

    public record VaultSnapshot(
            String snapshotId,
            long timestamp,
            int rawByteSize,
            int encryptedByteSize,
            String sha256Checksum,
            String ivHex
    ) {}

    private final List<VaultSnapshot> snapshotHistory = new ArrayList<>();

    public EncryptedBackupVault() {
        // Seed initial encrypted baseline snapshot
        createEncryptedSnapshot("DATABASE_BASELINE", "tasks:88;tx:53;goals:11;bookings:14;state:NORMAL".getBytes(StandardCharsets.UTF_8));
    }

    public VaultSnapshot createEncryptedSnapshot(String tag, byte[] plainData) {
        try {
            SecureRandom random = new SecureRandom();
            byte[] salt = new byte[16];
            byte[] iv = new byte[16];
            random.nextBytes(salt);
            random.nextBytes(iv);

            SecretKeyFactory factory = SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256");
            PBEKeySpec spec = new PBEKeySpec(MASTER_PASSPHRASE.toCharArray(), salt, ITERATIONS, KEY_LENGTH);
            SecretKey tmp = factory.generateSecret(spec);
            SecretKey secret = new SecretKeySpec(tmp.getEncoded(), "AES");

            Cipher cipher = Cipher.getInstance("AES/CBC/PKCS5Padding");
            cipher.init(Cipher.ENCRYPT_MODE, secret, new IvParameterSpec(iv));
            byte[] cipherText = cipher.doFinal(plainData);

            // Compute SHA-256 checksum of plaintext
            java.security.MessageDigest md = java.security.MessageDigest.getInstance("SHA-256");
            byte[] digest = md.digest(plainData);
            StringBuilder hexCheck = new StringBuilder();
            for (byte b : digest) {
                hexCheck.append(String.format("%02x", b));
            }

            StringBuilder hexIv = new StringBuilder();
            for (byte b : iv) {
                hexIv.append(String.format("%02x", b));
            }

            String snapId = "SNAP-" + System.currentTimeMillis() % 100000;
            VaultSnapshot snap = new VaultSnapshot(
                    snapId,
                    System.currentTimeMillis(),
                    plainData.length,
                    cipherText.length + salt.length + iv.length,
                    hexCheck.substring(0, 16) + "...",
                    hexIv.substring(0, 16)
            );

            snapshotHistory.add(0, snap);
            return snap;

        } catch (Exception e) {
            throw new RuntimeException("Vault encryption failure", e);
        }
    }

    public List<VaultSnapshot> getSnapshotHistory() {
        return Collections.unmodifiableList(snapshotHistory);
    }
}
