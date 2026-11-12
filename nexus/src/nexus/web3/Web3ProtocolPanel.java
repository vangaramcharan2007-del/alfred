package nexus.web3;

import javax.swing.*;
import java.awt.*;

public class Web3ProtocolPanel extends JPanel {
    private final Web3ProtocolService service = Web3ProtocolService.getInstance();
    private JTextField gradePayloadField;

    public Web3ProtocolPanel() {
        setLayout(new BorderLayout(10, 10));
        setBackground(new Color(15, 23, 42));
        setBorder(BorderFactory.createEmptyBorder(12, 12, 12, 12));

        // 1. TOP HEADER
        JPanel headerBar = new JPanel(new BorderLayout());
        headerBar.setBackground(new Color(30, 41, 59));
        headerBar.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createLineBorder(new Color(51, 65, 85)),
                BorderFactory.createEmptyBorder(8, 14, 8, 14)
        ));

        JLabel title = new JLabel("🌐 WEB3, ZERO-KNOWLEDGE PROOFS & VERIFIABLE CREDENTIALS (PHASE 12)");
        title.setFont(new Font("Consolas", Font.BOLD, 15));
        title.setForeground(new Color(56, 189, 248));

        JLabel authorityBadge = new JLabel("🔑 RSA-2048 & zk-SNARK CIPHER ENGINE ONLINE");
        authorityBadge.setFont(new Font("Segoe UI", Font.BOLD, 12));
        authorityBadge.setForeground(new Color(52, 211, 153));

        headerBar.add(title, BorderLayout.WEST);
        headerBar.add(authorityBadge, BorderLayout.EAST);
        add(headerBar, BorderLayout.NORTH);

        // 2. CENTER TABBED PROTOCOL PANELS
        JTabbedPane subTabs = new JTabbedPane();
        subTabs.setFont(new Font("Segoe UI", Font.BOLD, 12));

        subTabs.addTab("🛡️ zk-SNARK Zero-Knowledge Identity", createZkPanel());
        subTabs.addTab("🎟️ Soulbound POAP NFT Passes", createPoapPanel());
        subTabs.addTab("✍️ Faculty Review 2 Cryptographic Signer", createSignaturePanel());

        add(subTabs, BorderLayout.CENTER);

        // 3. BOTTOM HUD
        JPanel bottomBar = new JPanel(new FlowLayout(FlowLayout.LEFT, 18, 4));
        bottomBar.setBackground(new Color(30, 41, 59));
        bottomBar.setBorder(BorderFactory.createLineBorder(new Color(51, 65, 85)));

        JLabel pubKeyLabel = new JLabel("Faculty Reviewer Public Key: " + service.getFacultyPublicKeyHex());
        pubKeyLabel.setFont(new Font("Consolas", Font.PLAIN, 11));
        pubKeyLabel.setForeground(new Color(147, 197, 253));

        JLabel chainLabel = new JLabel("• Network: Polygon L2 zkEVM • Smart Contract: 0x9f4a...21c");
        chainLabel.setFont(new Font("Consolas", Font.PLAIN, 11));
        chainLabel.setForeground(new Color(52, 211, 153));

        bottomBar.add(pubKeyLabel);
        bottomBar.add(chainLabel);
        add(bottomBar, BorderLayout.SOUTH);
    }

    // --- SUBTAB 1: ZK-SNARK ---
    private JPanel createZkPanel() {
        JPanel p = new JPanel(new BorderLayout(10, 10));
        p.setBackground(new Color(24, 30, 42));
        p.setBorder(BorderFactory.createEmptyBorder(12, 14, 12, 14));

        JLabel desc = new JLabel("<html><b>Zero-Knowledge Student Identity Proof (Groth16 zk-SNARK)</b><br>" +
                "<font color='#94a3b8'>Proves active SRM student status & cinema discount qualification without exposing sensitive student PII (Name, Reg No, or Room No).</font></html>");
        desc.setFont(new Font("Segoe UI", Font.PLAIN, 12));
        desc.setForeground(Color.WHITE);
        p.add(desc, BorderLayout.NORTH);

        JTextArea console = new JTextArea();
        console.setEditable(false);
        console.setFont(new Font("Consolas", Font.PLAIN, 12));
        console.setBackground(new Color(10, 15, 30));
        console.setForeground(new Color(52, 211, 153));
        console.setText("""
                [zk-SNARK PROVER INITIALIZED]
                Poseidon Hash Tree Loaded. Proving Key: 2048-bit Groth16.
                Click 'Generate & Verify zk-SNARK Proof' to simulate cryptographic zero-knowledge assertion.
                -----------------------------------------------------------------------------------------
                """);
        p.add(new JScrollPane(console), BorderLayout.CENTER);

        JButton genBtn = new JButton("⚡ Generate & Verify Cryptographic zk-SNARK Proof");
        genBtn.setFont(new Font("Segoe UI", Font.BOLD, 12));
        genBtn.setBackground(new Color(16, 185, 129));
        genBtn.setForeground(Color.WHITE);
        genBtn.setFocusPainted(false);
        genBtn.setPreferredSize(new Dimension(300, 38));
        genBtn.addActionListener(e -> {
            Web3ProtocolService.ZkProofResult res = service.generateZkStudentProof("USER-01", "RA2511027010164");
            console.append(String.format("""
                    >>> PROOF COMPUTED IN %dms:
                    MERKLE ROOT   : %s
                    PROOF HASH    : %s
                    PUBLIC INPUTS : %s
                    VERIFICATION  : VALID (0%% PII Leaked to External Party)
                    STATUS        : DISCOUNT APPROVED BY ZERO-KNOWLEDGE PROOF!
                    -----------------------------------------------------------------------------------------
                    """, res.latencyMs(), res.merkleRoot(), res.proofHash(), res.publicInputs()));
            console.setCaretPosition(console.getDocument().getLength());
        });
        p.add(genBtn, BorderLayout.SOUTH);
        return p;
    }

    // --- SUBTAB 2: SOULBOUND POAP ---
    private JPanel createPoapPanel() {
        JPanel p = new JPanel(new BorderLayout(10, 10));
        p.setBackground(new Color(24, 30, 42));
        p.setBorder(BorderFactory.createEmptyBorder(12, 14, 12, 14));

        JLabel desc = new JLabel("<html><b>Soulbound Token (ERC-1155 POAP) Event Attendance Minter</b><br>" +
                "<font color='#94a3b8'>Mints non-transferable proof-of-attendance NFT tokens to student wallet upon cinema bookings or hackathon participation.</font></html>");
        desc.setFont(new Font("Segoe UI", Font.PLAIN, 12));
        desc.setForeground(Color.WHITE);
        p.add(desc, BorderLayout.NORTH);

        JTextArea console = new JTextArea();
        console.setEditable(false);
        console.setFont(new Font("Consolas", Font.PLAIN, 12));
        console.setBackground(new Color(10, 15, 30));
        console.setForeground(new Color(56, 189, 248));
        console.setText("""
                [SOULBOUND TOKEN MINTER]
                Connected to Polygon zkEVM Testnet.
                Student Wallet: 0x71C8492A02847183948bB5920491
                -----------------------------------------------------------------------------------------
                """);
        p.add(new JScrollPane(console), BorderLayout.CENTER);

        JPanel btnBar = new JPanel(new FlowLayout(FlowLayout.LEFT, 10, 0));
        btnBar.setOpaque(false);

        JButton mintCinema = new JButton("🎟️ Mint Interstellar IMAX Premiere POAP");
        mintCinema.setFont(new Font("Segoe UI", Font.BOLD, 11));
        mintCinema.setBackground(new Color(59, 130, 246));
        mintCinema.setForeground(Color.WHITE);
        mintCinema.addActionListener(e -> {
            Web3ProtocolService.PoapToken t = service.mintSoulboundPoap("Interstellar IMAX 3D Premiere", "0x71C8492A0284");
            console.append(String.format("""
                    >>> SOULBOUND POAP MINTED:
                    TOKEN ID  : %s
                    EVENT     : %s
                    RECIPIENT : %s
                    IPFS CID  : %s
                    BLOCK NUM : #%d (Confirmed on Polygon L2)
                    -----------------------------------------------------------------------------------------
                    """, t.tokenId(), t.eventName(), t.recipientAddress(), t.ipfsMetadata(), t.blockNumber()));
            console.setCaretPosition(console.getDocument().getLength());
        });

        JButton mintHackathon = new JButton("💻 Mint SRM Tech Hackathon 2026 POAP");
        mintHackathon.setFont(new Font("Segoe UI", Font.BOLD, 11));
        mintHackathon.setBackground(new Color(139, 92, 246));
        mintHackathon.setForeground(Color.WHITE);
        mintHackathon.addActionListener(e -> {
            Web3ProtocolService.PoapToken t = service.mintSoulboundPoap("SRM Tech Hackathon 2026 Winner", "0x71C8492A0284");
            console.append(String.format("""
                    >>> SOULBOUND POAP MINTED:
                    TOKEN ID  : %s
                    EVENT     : %s
                    RECIPIENT : %s
                    IPFS CID  : %s
                    BLOCK NUM : #%d (Confirmed on Polygon L2)
                    -----------------------------------------------------------------------------------------
                    """, t.tokenId(), t.eventName(), t.recipientAddress(), t.ipfsMetadata(), t.blockNumber()));
            console.setCaretPosition(console.getDocument().getLength());
        });

        btnBar.add(mintCinema);
        btnBar.add(mintHackathon);
        p.add(btnBar, BorderLayout.SOUTH);
        return p;
    }

    // --- SUBTAB 3: FACULTY SIGNATURE ---
    private JPanel createSignaturePanel() {
        JPanel p = new JPanel(new BorderLayout(10, 8));
        p.setBackground(new Color(24, 30, 42));
        p.setBorder(BorderFactory.createEmptyBorder(12, 14, 12, 14));

        JLabel desc = new JLabel("<html><b>Faculty Examiner Review 2 Cryptographic Signature & Anti-Tamper Engine</b><br>" +
                "<font color='#94a3b8'>Verifies evaluation grades signed by Dr. Academic Examiner's private key using RSA-2048 public-key cryptography.</font></html>");
        desc.setFont(new Font("Segoe UI", Font.PLAIN, 12));
        desc.setForeground(Color.WHITE);
        p.add(desc, BorderLayout.NORTH);

        JPanel centerPanel = new JPanel(new BorderLayout(0, 6));
        centerPanel.setOpaque(false);

        JPanel inputRow = new JPanel(new BorderLayout(6, 0));
        inputRow.setOpaque(false);
        JLabel l = new JLabel("Signed Academic Grade Payload:");
        l.setFont(new Font("Segoe UI", Font.BOLD, 11));
        l.setForeground(new Color(203, 213, 225));

        gradePayloadField = new JTextField(service.getLastSignedGradePayload());
        gradePayloadField.setFont(new Font("Consolas", Font.BOLD, 12));
        gradePayloadField.setBackground(new Color(15, 23, 42));
        gradePayloadField.setForeground(new Color(52, 211, 153));
        gradePayloadField.setBorder(BorderFactory.createLineBorder(new Color(51, 65, 85)));

        inputRow.add(l, BorderLayout.NORTH);
        inputRow.add(gradePayloadField, BorderLayout.CENTER);
        centerPanel.add(inputRow, BorderLayout.NORTH);

        JTextArea console = new JTextArea();
        console.setEditable(false);
        console.setFont(new Font("Consolas", Font.PLAIN, 12));
        console.setBackground(new Color(10, 15, 30));
        console.setForeground(new Color(52, 211, 153));
        console.setText("""
                [FACULTY ASYMMETRIC VERIFIER READY]
                Signer: Dr. Academic Examiner (Faculty Evaluator)
                Algorithm: SHA256withRSA (2048-bit Private Key)
                -----------------------------------------------------------------------------------------
                """);
        centerPanel.add(new JScrollPane(console), BorderLayout.CENTER);
        p.add(centerPanel, BorderLayout.CENTER);

        JPanel btnRow = new JPanel(new FlowLayout(FlowLayout.RIGHT, 10, 0));
        btnRow.setOpaque(false);

        JButton verifyBtn = new JButton("✓ Verify Cryptographic Signature");
        verifyBtn.setFont(new Font("Segoe UI", Font.BOLD, 11));
        verifyBtn.setBackground(new Color(16, 185, 129));
        verifyBtn.setForeground(Color.WHITE);
        verifyBtn.addActionListener(e -> {
            String text = gradePayloadField.getText();
            boolean valid = service.verifyEvaluation(text, service.getLastSignatureBase64());
            if (valid) {
                console.append(String.format("""
                        >>> ASYMMETRIC SIGNATURE VERIFICATION: SUCCESS!
                        PAYLOAD     : %s
                        SIGNER      : Dr. Academic Examiner
                        PUBLIC KEY  : %s
                        SIGNATURE   : %s...
                        RESULT      : 100%% AUTHENTIC & UNTAMPERED GRADE CONFIRMED.
                        -----------------------------------------------------------------------------------------
                        """, text, service.getFacultyPublicKeyHex(), service.getLastSignatureBase64().substring(0, 32)));
            } else {
                console.append(String.format("""
                        >>> CRITICAL ALERT: SIGNATURE VERIFICATION FAILED!
                        PAYLOAD     : %s
                        RESULT      : TAMPERING DETECTED! Content does not match Faculty Signature!
                        -----------------------------------------------------------------------------------------
                        """, text));
            }
            console.setCaretPosition(console.getDocument().getLength());
        });

        JButton tamperBtn = new JButton("🚫 Simulate Tampered Grade (Change to 101/100)");
        tamperBtn.setFont(new Font("Segoe UI", Font.BOLD, 11));
        tamperBtn.setBackground(new Color(220, 38, 38));
        tamperBtn.setForeground(Color.WHITE);
        tamperBtn.addActionListener(e -> {
            gradePayloadField.setText(service.getLastSignedGradePayload().replace("100/100", "101/100 (TAMPERED)"));
            console.append("""
                    [SIMULATION] Tampered grade payload injected into verify buffer.
                    Click 'Verify Cryptographic Signature' to test cryptographic integrity check!
                    -----------------------------------------------------------------------------------------
                    """);
            console.setCaretPosition(console.getDocument().getLength());
        });

        JButton resetBtn = new JButton("Reset Original");
        resetBtn.setFont(new Font("Segoe UI", Font.PLAIN, 11));
        resetBtn.addActionListener(e -> {
            gradePayloadField.setText(service.getLastSignedGradePayload());
        });

        btnRow.add(resetBtn);
        btnRow.add(tamperBtn);
        btnRow.add(verifyBtn);
        p.add(btnRow, BorderLayout.SOUTH);

        return p;
    }
}