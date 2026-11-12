package nexus.vault;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

/**
 * Immutable SHA-256 Rolling Ledger Hash Chain.
 * 
 * Author: Ram Charan Vanga (Reg No: RA2511027010164)
 * Department of Computer Science & Engineering
 * SRM Institute of Science and Technology, Kattankulathur
 */
public class ImmutableAuditChain {
    private static final String GENESIS_PREV_HASH = "0000000000000000000000000000000000000000000000000000000000000000";
    private final List<AuditBlock> chain = new ArrayList<>();

    public ImmutableAuditChain() {
        // Genesis block
        AuditBlock genesis = new AuditBlock(
                0,
                GENESIS_PREV_HASH,
                "TX-GENESIS",
                "NEXUS V9 Master Ledger Initialized (SRM IST Kattankulathur)",
                10000.00,
                System.currentTimeMillis() - 86400000L
        );
        chain.add(genesis);
        seedInitialTransactions();
    }

    private void seedInitialTransactions() {
        addTransaction("TX-1001", "Kaveri Hostel Mess Fee Advance", 3500.00);
        addTransaction("TX-1002", "SRM Tech Park Library Resource Fee", 450.00);
        addTransaction("TX-1003", "Java Enterprise Cloud Lab Access", 850.00);
        addTransaction("TX-1004", "BookMyShow Inox Potheri Cinema Ticket", 525.00);
    }

    public synchronized AuditBlock addTransaction(String txId, String description, double amount) {
        AuditBlock prev = chain.get(chain.size() - 1);
        AuditBlock newBlock = new AuditBlock(
                chain.size(),
                prev.getCurrentHash(),
                txId,
                description,
                amount,
                System.currentTimeMillis()
        );
        chain.add(newBlock);
        return newBlock;
    }

    public static class ChainVerificationResult {
        public final boolean isValid;
        public final int totalBlocks;
        public final int corruptedBlockIndex;
        public final String message;

        public ChainVerificationResult(boolean isValid, int totalBlocks, int corruptedBlockIndex, String message) {
            this.isValid = isValid;
            this.totalBlocks = totalBlocks;
            this.corruptedBlockIndex = corruptedBlockIndex;
            this.message = message;
        }
    }

    public synchronized ChainVerificationResult verifyIntegrity() {
        for (int i = 0; i < chain.size(); i++) {
            AuditBlock current = chain.get(i);

            // 1. Check current hash matches calculated hash
            String recalculated = current.calculateHash();
            if (!recalculated.equals(current.getCurrentHash())) {
                return new ChainVerificationResult(
                        false, chain.size(), i,
                        String.format("Data corruption at Block #%d! Stored hash %s does not match recalculated %s",
                                i, current.getCurrentHash().substring(0, 12), recalculated.substring(0, 12))
                );
            }

            // 2. Check previous hash links
            if (i > 0) {
                AuditBlock prev = chain.get(i - 1);
                if (!current.getPreviousHash().equals(prev.getCurrentHash())) {
                    return new ChainVerificationResult(
                            false, chain.size(), i,
                            String.format("Broken chain link at Block #%d! Expected previous hash %s, found %s",
                                    i, prev.getCurrentHash().substring(0, 12), current.getPreviousHash().substring(0, 12))
                    );
                }
            }
        }

        return new ChainVerificationResult(
                true, chain.size(), -1,
                String.format("All %d blocks cryptographically verified. Mathematical integrity 100%% intact.", chain.size())
        );
    }

    public synchronized List<AuditBlock> getChain() {
        return Collections.unmodifiableList(new ArrayList<>(chain));
    }

    public synchronized int getChainLength() {
        return chain.size();
    }

    public synchronized String getHeadHash() {
        return chain.isEmpty() ? GENESIS_PREV_HASH : chain.get(chain.size() - 1).getCurrentHash();
    }
}
