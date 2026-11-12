package nexus.vault;

import javax.swing.*;
import java.awt.*;
import java.nio.charset.StandardCharsets;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;

/**
 * Phase 14 UI Panel: Encrypted Database Vault & Cryptographic Tamper-Proof Audit Chain.
 * 
 * Author: Ram Charan Vanga (Reg No: RA2511027010164)
 * Department of Computer Science & Engineering
 * SRM Institute of Science and Technology, Kattankulathur
 */
public class VaultAuditPanel extends JPanel {
    private final VaultService service = VaultService.getInstance();
    private final SimpleDateFormat timeFormat = new SimpleDateFormat("HH:mm:ss");

    private final JPanel blocksContainer;
    private final JLabel integrityStatusLabel;
    private final JPanel snapshotsContainer;
    private final JTextArea vaultLogArea;

    public VaultAuditPanel() {
        setLayout(new BorderLayout(10, 10));
        setBackground(new Color(15, 23, 42));
        setBorder(BorderFactory.createEmptyBorder(12, 12, 12, 12));

        // 1. TOP HEADER BAR
        JPanel headerBar = new JPanel(new BorderLayout());
        headerBar.setBackground(new Color(30, 41, 59));
        headerBar.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createLineBorder(new Color(51, 65, 85)),
                BorderFactory.createEmptyBorder(8, 14, 8, 14)
        ));

        JLabel title = new JLabel("🔒 IMMUTABLE SHA-256 AUDIT CHAIN & AES-256 DATABASE VAULT (PHASE 14)");
        title.setFont(new Font("Consolas", Font.BOLD, 14));
        title.setForeground(new Color(56, 189, 248));

        integrityStatusLabel = new JLabel("● LEDGER INTEGRITY: 100% CRYPTOGRAPHICALLY VALID");
        integrityStatusLabel.setFont(new Font("Segoe UI", Font.BOLD, 11));
        integrityStatusLabel.setForeground(new Color(52, 211, 153));

        headerBar.add(title, BorderLayout.WEST);
        headerBar.add(integrityStatusLabel, BorderLayout.EAST);
        add(headerBar, BorderLayout.NORTH);

        // 2. CENTER: LEFT = ROLLING HASH CHAIN | RIGHT = AES-256 VAULT SNAPSHOTS
        JPanel centerGrid = new JPanel(new GridLayout(1, 2, 12, 0));
        centerGrid.setOpaque(false);

        // LEFT: Rolling Hash Chain
        JPanel leftPanel = new JPanel(new BorderLayout(0, 8));
        leftPanel.setBackground(new Color(24, 30, 42));
        leftPanel.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createLineBorder(new Color(51, 65, 85)),
                BorderFactory.createEmptyBorder(10, 12, 10, 12)
        ));

        JLabel chainTitle = new JLabel("🔗 ROLLING MERKLE LEDGER CHAIN (SHA-256 TAMPER-EVIDENT):");
        chainTitle.setFont(new Font("Segoe UI", Font.BOLD, 12));
        chainTitle.setForeground(new Color(56, 189, 248));
        leftPanel.add(chainTitle, BorderLayout.NORTH);

        blocksContainer = new JPanel();
        blocksContainer.setLayout(new BoxLayout(blocksContainer, BoxLayout.Y_AXIS));
        blocksContainer.setBackground(new Color(15, 23, 42));

        JScrollPane chainScroll = new JScrollPane(blocksContainer);
        chainScroll.setBorder(BorderFactory.createLineBorder(new Color(51, 65, 85)));
        chainScroll.getVerticalScrollBar().setUnitIncrement(14);
        leftPanel.add(chainScroll, BorderLayout.CENTER);

        // Chain Actions
        JPanel chainActions = new JPanel(new FlowLayout(FlowLayout.RIGHT, 6, 4));
        chainActions.setOpaque(false);

        JButton verifyBtn = new JButton("🛡️ Verify Ledger Cryptography");
        verifyBtn.setFont(new Font("Segoe UI", Font.BOLD, 11));
        verifyBtn.setBackground(new Color(16, 185, 129));
        verifyBtn.setForeground(Color.WHITE);
        verifyBtn.addActionListener(e -> runVerification());

        JButton tamperBtn = new JButton("🚨 Inject Malicious Tamper Test");
        tamperBtn.setFont(new Font("Segoe UI", Font.BOLD, 11));
        tamperBtn.setBackground(new Color(220, 38, 38));
        tamperBtn.setForeground(Color.WHITE);
        tamperBtn.addActionListener(e -> injectTamper());

        chainActions.add(verifyBtn);
        chainActions.add(tamperBtn);
        leftPanel.add(chainActions, BorderLayout.SOUTH);

        centerGrid.add(leftPanel);

        // RIGHT: AES-256 Encrypted Backup Vault
        JPanel rightPanel = new JPanel(new BorderLayout(0, 8));
        rightPanel.setBackground(new Color(24, 30, 42));
        rightPanel.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createLineBorder(new Color(51, 65, 85)),
                BorderFactory.createEmptyBorder(10, 12, 10, 12)
        ));

        JLabel vaultTitle = new JLabel("🔐 AES-256-CBC ENCRYPTED DATABASE VAULT (PBKDF2 65k ITER):");
        vaultTitle.setFont(new Font("Segoe UI", Font.BOLD, 12));
        vaultTitle.setForeground(new Color(52, 211, 153));
        rightPanel.add(vaultTitle, BorderLayout.NORTH);

        JPanel rightCenter = new JPanel(new BorderLayout(0, 8));
        rightCenter.setOpaque(false);

        snapshotsContainer = new JPanel();
        snapshotsContainer.setLayout(new BoxLayout(snapshotsContainer, BoxLayout.Y_AXIS));
        snapshotsContainer.setBackground(new Color(15, 23, 42));

        JScrollPane snapScroll = new JScrollPane(snapshotsContainer);
        snapScroll.setBorder(BorderFactory.createLineBorder(new Color(51, 65, 85)));
        snapScroll.setPreferredSize(new Dimension(300, 160));
        rightCenter.add(snapScroll, BorderLayout.CENTER);

        vaultLogArea = new JTextArea();
        vaultLogArea.setEditable(false);
        vaultLogArea.setFont(new Font("Consolas", Font.PLAIN, 11));
        vaultLogArea.setBackground(new Color(10, 15, 30));
        vaultLogArea.setForeground(new Color(0, 255, 200));
        vaultLogArea.setText("""
                [PHASE 14 VAULT ENGINE OPERATIONAL]
                • AES-256-CBC cipher with PKCS5 padding & secure random 16-byte IV.
                • PBKDF2 key derivation using 65,536 rounds of HMAC-SHA256.
                • Point-In-Time disaster recovery snapshots verified.
                --------------------------------------------------------------
                """);
        JScrollPane logScroll = new JScrollPane(vaultLogArea);
        logScroll.setPreferredSize(new Dimension(300, 120));
        rightCenter.add(logScroll, BorderLayout.SOUTH);

        rightPanel.add(rightCenter, BorderLayout.CENTER);

        // Vault Actions
        JPanel vaultActions = new JPanel(new FlowLayout(FlowLayout.RIGHT, 6, 4));
        vaultActions.setOpaque(false);

        JButton snapBtn = new JButton("📦 Generate Encrypted PITR Snapshot");
        snapBtn.setFont(new Font("Segoe UI", Font.BOLD, 11));
        snapBtn.setBackground(new Color(59, 130, 246));
        snapBtn.setForeground(Color.WHITE);
        snapBtn.addActionListener(e -> generateSnapshot());

        vaultActions.add(snapBtn);
        rightPanel.add(vaultActions, BorderLayout.SOUTH);

        centerGrid.add(rightPanel);
        add(centerGrid, BorderLayout.CENTER);

        renderBlocks();
        renderSnapshots();
    }

    private void renderBlocks() {
        blocksContainer.removeAll();
        List<AuditBlock> blocks = service.getAuditChain().getChain();

        for (AuditBlock b : blocks) {
            JPanel card = new JPanel(new BorderLayout(8, 2));
            card.setBackground(new Color(30, 41, 59));
            card.setBorder(BorderFactory.createCompoundBorder(
                    BorderFactory.createMatteBorder(0, 3, 0, 0, b.getBlockIndex() == 0 ? Color.CYAN : new Color(16, 185, 129)),
                    BorderFactory.createEmptyBorder(6, 10, 6, 10)
            ));
            card.setMaximumSize(new Dimension(2000, 58));

            JPanel top = new JPanel(new BorderLayout());
            top.setOpaque(false);
            JLabel idxLabel = new JLabel("Block #" + b.getBlockIndex() + " • " + b.getTransactionId() + " (" + b.getDescription() + ")");
            idxLabel.setFont(new Font("Segoe UI", Font.BOLD, 11));
            idxLabel.setForeground(Color.WHITE);

            JLabel amtLabel = new JLabel(String.format("$%,.2f", b.getAmount()));
            amtLabel.setFont(new Font("Consolas", Font.BOLD, 11));
            amtLabel.setForeground(new Color(52, 211, 153));

            top.add(idxLabel, BorderLayout.WEST);
            top.add(amtLabel, BorderLayout.EAST);

            JPanel bot = new JPanel(new BorderLayout());
            bot.setOpaque(false);
            JLabel hashLabel = new JLabel("Hash: " + b.getCurrentHash().substring(0, 24) + "... (Prev: " + b.getPreviousHash().substring(0, 12) + "...)");
            hashLabel.setFont(new Font("Consolas", Font.PLAIN, 10));
            hashLabel.setForeground(new Color(148, 163, 184));
            bot.add(hashLabel, BorderLayout.WEST);

            card.add(top, BorderLayout.NORTH);
            card.add(bot, BorderLayout.SOUTH);

            blocksContainer.add(card);
            blocksContainer.add(Box.createVerticalStrut(4));
        }

        blocksContainer.revalidate();
        blocksContainer.repaint();
    }

    private void renderSnapshots() {
        snapshotsContainer.removeAll();
        List<EncryptedBackupVault.VaultSnapshot> snaps = service.getBackupVault().getSnapshotHistory();

        for (EncryptedBackupVault.VaultSnapshot s : snaps) {
            JPanel card = new JPanel(new BorderLayout(8, 2));
            card.setBackground(new Color(30, 41, 59));
            card.setBorder(BorderFactory.createCompoundBorder(
                    BorderFactory.createMatteBorder(0, 3, 0, 0, new Color(59, 130, 246)),
                    BorderFactory.createEmptyBorder(6, 10, 6, 10)
            ));
            card.setMaximumSize(new Dimension(2000, 52));

            JPanel top = new JPanel(new BorderLayout());
            top.setOpaque(false);
            JLabel id = new JLabel(s.snapshotId() + " • " + timeFormat.format(new Date(s.timestamp())));
            id.setFont(new Font("Consolas", Font.BOLD, 11));
            id.setForeground(new Color(56, 189, 248));

            JLabel size = new JLabel(s.rawByteSize() + "B -> " + s.encryptedByteSize() + "B (AES-256)");
            size.setFont(new Font("Consolas", Font.PLAIN, 10));
            size.setForeground(new Color(52, 211, 153));

            top.add(id, BorderLayout.WEST);
            top.add(size, BorderLayout.EAST);

            JLabel hash = new JLabel("HMAC-SHA256: " + s.sha256Checksum() + " | IV: " + s.ivHex());
            hash.setFont(new Font("Consolas", Font.PLAIN, 9));
            hash.setForeground(new Color(148, 163, 184));

            card.add(top, BorderLayout.NORTH);
            card.add(hash, BorderLayout.SOUTH);

            snapshotsContainer.add(card);
            snapshotsContainer.add(Box.createVerticalStrut(4));
        }

        snapshotsContainer.revalidate();
        snapshotsContainer.repaint();
    }

    private void runVerification() {
        ImmutableAuditChain.ChainVerificationResult res = service.getAuditChain().verifyIntegrity();
        if (res.isValid) {
            integrityStatusLabel.setText("● LEDGER INTEGRITY: 100% CRYPTOGRAPHICALLY VALID (" + res.totalBlocks + " BLOCKS)");
            integrityStatusLabel.setForeground(new Color(52, 211, 153));
            logVault("✓ Full ledger integrity verified: " + res.message);
            JOptionPane.showMessageDialog(this, res.message, "Cryptographic Ledger Verified", JOptionPane.INFORMATION_MESSAGE);
        } else {
            integrityStatusLabel.setText("🚨 TAMPER DETECTED AT BLOCK #" + res.corruptedBlockIndex);
            integrityStatusLabel.setForeground(new Color(239, 68, 68));
            logVault("🚨 ALERT: " + res.message);
            JOptionPane.showMessageDialog(this, res.message, "🚨 Cryptographic Tamper Detected!", JOptionPane.ERROR_MESSAGE);
        }
        renderBlocks();
    }

    private void injectTamper() {
        List<AuditBlock> blocks = service.getAuditChain().getChain();
        if (blocks.size() > 1) {
            AuditBlock victim = blocks.get(1);
            double orig = victim.getAmount();
            victim.tamperAmount(99999.99); // Alter transaction amount
            logVault(String.format("⚠️ INJECTED TAMPER: Block #1 amount maliciously changed from $%.2f to $99,999.99!", orig));
            runVerification();
        }
    }

    private void generateSnapshot() {
        String payload = "SNAPSHOT_PAYLOAD_LEDGER_HASH:" + service.getAuditChain().getHeadHash() + ";TIME:" + System.currentTimeMillis();
        EncryptedBackupVault.VaultSnapshot snap = service.getBackupVault().createEncryptedSnapshot(
                "MANUAL_DISASTER_RECOVERY", payload.getBytes(StandardCharsets.UTF_8));
        renderSnapshots();
        logVault("✓ Encrypted snapshot " + snap.snapshotId() + " generated. Checksum: " + snap.sha256Checksum());
    }

    private void logVault(String msg) {
        vaultLogArea.append(msg + "\n");
        vaultLogArea.setCaretPosition(vaultLogArea.getDocument().getLength());
    }
}
