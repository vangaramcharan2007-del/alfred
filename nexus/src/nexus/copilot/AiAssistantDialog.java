package nexus.copilot;

import javax.swing.*;
import java.awt.*;
import java.awt.event.KeyAdapter;
import java.awt.event.KeyEvent;
import java.text.SimpleDateFormat;
import java.util.Date;

/**
 * Interactive Strategy Advisor Dialog - Real-Time Campus & Financial Optimization.
 * 
 * Author: Ram Charan Vanga (Reg No: RA2511027010164)
 * Department of Computer Science & Engineering
 * SRM Institute of Science and Technology, Kattankulathur
 */
public class AiAssistantDialog extends JDialog {
    private final JTextArea conversationArea;
    private final JTextField inputField;
    private final JButton sendButton;
    private final JLabel statusLabel;
    private final SimpleDateFormat timeFormat = new SimpleDateFormat("HH:mm:ss");

    public AiAssistantDialog(Frame owner) {
        super(owner, "⚡ NEXUS Campus Strategy Advisor - SRM Edition", false);
        setSize(680, 560);
        setLocationRelativeTo(owner);
        setLayout(new BorderLayout(0, 0));

        JPanel mainPanel = new JPanel(new BorderLayout(10, 10));
        mainPanel.setBackground(new Color(15, 23, 42));
        mainPanel.setBorder(BorderFactory.createEmptyBorder(12, 14, 12, 14));

        // 1. TOP HEADER & PROMPT PILLS
        JPanel topPanel = new JPanel(new BorderLayout(0, 8));
        topPanel.setOpaque(false);

        JPanel headerBar = new JPanel(new BorderLayout());
        headerBar.setOpaque(false);

        JLabel titleLabel = new JLabel("💡 SRM CAMPUS STRATEGY & FINANCIAL ADVISOR");
        titleLabel.setFont(new Font("Segoe UI", Font.BOLD, 14));
        titleLabel.setForeground(new Color(56, 189, 248));

        statusLabel = new JLabel("● Advisory Core: Online (Latency ~1.2s)");
        statusLabel.setFont(new Font("Segoe UI", Font.BOLD, 11));
        statusLabel.setForeground(new Color(52, 211, 153));

        headerBar.add(titleLabel, BorderLayout.WEST);
        headerBar.add(statusLabel, BorderLayout.EAST);
        topPanel.add(headerBar, BorderLayout.NORTH);

        // Quick Suggestion Chips
        JPanel chipsPanel = new JPanel(new FlowLayout(FlowLayout.LEFT, 6, 2));
        chipsPanel.setOpaque(false);

        chipsPanel.add(createChip("💡 SRM Student Budget Plan", "Give me a practical monthly budget strategy for a student living in Kaveri Hostel SRM with 10k allowance."));
        chipsPanel.add(createChip("🎬 Weekend Movie Deals", "What are the best movies to watch this weekend near SRM Kattankulathur with student discounts?"));
        chipsPanel.add(createChip("📈 SIP Compound Calculator", "If I invest ₹1,500/month in a student SIP at 13% CAGR, what will it be worth in 4 years?"));
        chipsPanel.add(createChip("⚡ Outflow Optimization", "How can I cut my daily canteen and swiggy spending without sacrificing nutrition?"));

        topPanel.add(chipsPanel, BorderLayout.SOUTH);
        mainPanel.add(topPanel, BorderLayout.NORTH);

        // 2. CENTER CONVERSATION LOG
        conversationArea = new JTextArea();
        conversationArea.setEditable(false);
        conversationArea.setFont(new Font("Segoe UI", Font.PLAIN, 13));
        conversationArea.setBackground(new Color(24, 30, 42));
        conversationArea.setForeground(new Color(226, 232, 240));
        conversationArea.setLineWrap(true);
        conversationArea.setWrapStyleWord(true);
        conversationArea.setMargin(new Insets(10, 12, 10, 12));

        // Initial welcome message
        conversationArea.setText("""
                💡 [NEXUS SMART ADVISORY CORE ONLINE]
                Welcome to your SRM Campus & Financial Optimization Assistant.
                Select an optimization strategy above or enter any campus/financial question:
                --------------------------------------------------------------------------------------
                """);

        JScrollPane scrollPane = new JScrollPane(conversationArea);
        scrollPane.setBorder(BorderFactory.createLineBorder(new Color(51, 65, 85)));
        scrollPane.getVerticalScrollBar().setUnitIncrement(14);
        mainPanel.add(scrollPane, BorderLayout.CENTER);

        // 3. BOTTOM INPUT BAR
        JPanel bottomPanel = new JPanel(new BorderLayout(8, 0));
        bottomPanel.setOpaque(false);
        bottomPanel.setBorder(BorderFactory.createEmptyBorder(6, 0, 0, 0));

        inputField = new JTextField();
        inputField.setFont(new Font("Segoe UI", Font.PLAIN, 13));
        inputField.setBackground(new Color(30, 41, 59));
        inputField.setForeground(Color.WHITE);
        inputField.setCaretColor(Color.CYAN);
        inputField.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createLineBorder(new Color(71, 85, 105)),
                BorderFactory.createEmptyBorder(6, 10, 6, 10)
        ));

        inputField.addKeyListener(new KeyAdapter() {
            @Override
            public void keyPressed(KeyEvent e) {
                if (e.getKeyCode() == KeyEvent.VK_ENTER) {
                    processUserInput();
                }
            }
        });

        sendButton = new JButton("Consult Advisor ⚡");
        sendButton.setFont(new Font("Segoe UI", Font.BOLD, 12));
        sendButton.setBackground(new Color(16, 185, 129));
        sendButton.setForeground(Color.WHITE);
        sendButton.setFocusPainted(false);
        sendButton.setCursor(new Cursor(Cursor.HAND_CURSOR));
        sendButton.addActionListener(e -> processUserInput());

        bottomPanel.add(inputField, BorderLayout.CENTER);
        bottomPanel.add(sendButton, BorderLayout.EAST);
        mainPanel.add(bottomPanel, BorderLayout.SOUTH);

        add(mainPanel);
    }

    private JButton createChip(String label, String prompt) {
        JButton btn = new JButton(label);
        btn.setFont(new Font("Segoe UI", Font.PLAIN, 11));
        btn.setBackground(new Color(30, 41, 59));
        btn.setForeground(new Color(147, 197, 253));
        btn.setFocusPainted(false);
        btn.setCursor(new Cursor(Cursor.HAND_CURSOR));
        btn.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createLineBorder(new Color(51, 65, 85)),
                BorderFactory.createEmptyBorder(3, 8, 3, 8)
        ));
        btn.addActionListener(e -> {
            inputField.setText(prompt);
            processUserInput();
        });
        return btn;
    }

    private void processUserInput() {
        String query = inputField.getText().trim();
        if (query.isEmpty()) return;

        inputField.setText("");
        inputField.setEnabled(false);
        sendButton.setEnabled(false);
        statusLabel.setText("● Advisory Core: Optimizing...");
        statusLabel.setForeground(new Color(251, 191, 36));

        String time = timeFormat.format(new Date());
        conversationArea.append(String.format("\n\n[%s] 👤 You:\n%s\n", time, query));
        conversationArea.append("\n💡 NEXUS Advisor: [Calculating strategy...]\n");
        conversationArea.setCaretPosition(conversationArea.getDocument().getLength());

        // Background worker execution
        new Thread(() -> {
            String context = "You are the NEXUS Campus Strategy & Financial Advisor for Ram Charan Vanga (SRM University student). " +
                             "Provide crisp, expert, encouraging advice for campus life, finance, cinema, and productivity in clean bullet points.";
            String answer = NexusAiClient.queryAi(query, context);

            SwingUtilities.invokeLater(() -> {
                // Remove the "[Calculating strategy...]" placeholder
                String current = conversationArea.getText();
                int idx = current.lastIndexOf("💡 NEXUS Advisor: [Calculating strategy...]");
                if (idx != -1) {
                    conversationArea.setText(current.substring(0, idx));
                }
                conversationArea.append("💡 NEXUS Advisor:\n" + answer.trim() + "\n");
                conversationArea.setCaretPosition(conversationArea.getDocument().getLength());

                inputField.setEnabled(true);
                sendButton.setEnabled(true);
                inputField.requestFocusInWindow();
                statusLabel.setText("● Advisory Core: Online (Ready)");
                statusLabel.setForeground(new Color(52, 211, 153));
            });
        }).start();
    }
}
