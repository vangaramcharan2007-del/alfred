package nexus.vault;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;

/**
 * Immutable Cryptographic Audit Block in the Rolling Hash Chain.
 * 
 * Author: Ram Charan Vanga (Reg No: RA2511027010164)
 * Department of Computer Science & Engineering
 * SRM Institute of Science and Technology, Kattankulathur
 */
public class AuditBlock {
    private final int blockIndex;
    private final String previousHash;
    private final String transactionId;
    private final String description;
    private final double amount;
    private final long timestamp;
    private String currentHash;

    public AuditBlock(int blockIndex, String previousHash, String transactionId, String description, double amount, long timestamp) {
        this.blockIndex = blockIndex;
        this.previousHash = previousHash;
        this.transactionId = transactionId;
        this.description = description;
        this.amount = amount;
        this.timestamp = timestamp;
        this.currentHash = calculateHash();
    }

    public String calculateHash() {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            String data = blockIndex + previousHash + transactionId + description + String.format("%.2f", amount) + timestamp;
            byte[] hash = digest.digest(data.getBytes(StandardCharsets.UTF_8));
            StringBuilder hexString = new StringBuilder();
            for (byte b : hash) {
                String hex = Integer.toHexString(0xff & b);
                if (hex.length() == 1) hexString.append('0');
                hexString.append(hex);
            }
            return hexString.toString();
        } catch (Exception e) {
            throw new RuntimeException("SHA-256 not available", e);
        }
    }

    public void tamperAmount(double fraudulentAmount) {
        // Intentionally corrupt block data to demonstrate cryptographic tamper detection
        try {
            java.lang.reflect.Field field = this.getClass().getDeclaredField("amount");
            field.setAccessible(true);
            field.setDouble(this, fraudulentAmount);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public int getBlockIndex() { return blockIndex; }
    public String getPreviousHash() { return previousHash; }
    public String getTransactionId() { return transactionId; }
    public String getDescription() { return description; }
    public double getAmount() { return amount; }
    public long getTimestamp() { return timestamp; }
    public String getCurrentHash() { return currentHash; }
}
