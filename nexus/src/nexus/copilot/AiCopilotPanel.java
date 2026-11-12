package nexus.copilot;

import javax.swing.*;
import java.awt.*;
import java.util.List;

public class AiCopilotPanel extends JPanel {
    private final AiCopilotService service = AiCopilotService.getInstance();
    private final JPanel agentsContainer;
    private final JTextArea commandOutputArea;
    private final JTextField commandInput;
    private final JPanel chartPanel;

    public AiCopilotPanel() {
        setLayout(new BorderLayout(10, 10));
        setBackground(new Color(15, 23, 42));
        setBorder(BorderFactory.createEmptyBorder(12, 12, 12, 12));

        // 1. TOP HEADER & AGENT CARDS
        JPanel topContainer = new JPanel(new BorderLayout(0, 10));
        topContainer.setOpaque(false);

        JPanel headerBar = new JPanel(new BorderLayout());
        headerBar.setBackground(new Color(30, 41, 59));
        headerBar.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createLineBorder(new Color(51, 65, 85)),
                BorderFactory.createEmptyBorder(8, 14, 8, 14)
        ));

        JLabel title = new JLabel("📈 AUTONOMOUS QUANTITATIVE FINANCIAL CORE & LSTM ENGINE (PHASE 10)");
        title.setFont(new Font("Consolas", Font.BOLD, 15));
        title.setForeground(new Color(56, 189, 248));

        JLabel modeBadge = new JLabel("⚡ FULLY AUTONOMOUS BACKGROUND OPERATION");
        modeBadge.setFont(new Font("Segoe UI", Font.BOLD, 12));
        modeBadge.setForeground(new Color(52, 211, 153));

        headerBar.add(title, BorderLayout.WEST);
        headerBar.add(modeBadge, BorderLayout.EAST);
        topContainer.add(headerBar, BorderLayout.NORTH);

        // 3 Agent Intelligence Cards
        agentsContainer = new JPanel(new GridLayout(1, 3, 10, 0));
        agentsContainer.setOpaque(false);
        renderAgentCards();
        topContainer.add(agentsContainer, BorderLayout.CENTER);

        add(topContainer, BorderLayout.NORTH);

        // 2. CENTER: LEFT = 30-DAY RUNWAY CHART | RIGHT = INTERACTIVE COMMAND CONSOLE
        JPanel centerGrid = new JPanel(new GridLayout(1, 2, 12, 0));
        centerGrid.setOpaque(false);

        // LEFT: 30-Day Predictive Runway Chart
        JPanel chartCard = new JPanel(new BorderLayout(0, 6));
        chartCard.setBackground(new Color(24, 30, 42));
        chartCard.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createLineBorder(new Color(51, 65, 85)),
                BorderFactory.createEmptyBorder(10, 12, 10, 12)
        ));

        JLabel chartTitle = new JLabel("📈 30-DAY FORWARD CASH RUNWAY PROJECTION (LSTM)");
        chartTitle.setFont(new Font("Segoe UI", Font.BOLD, 12));
        chartTitle.setForeground(new Color(56, 189, 248));
        chartCard.add(chartTitle, BorderLayout.NORTH);

        chartPanel = new JPanel() {
            @Override
            protected void paintComponent(Graphics g) {
                super.paintComponent(g);
                Graphics2D g2 = (Graphics2D) g;
                g2.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);

                int w = getWidth();
                int h = getHeight();

                // Background
                g2.setColor(new Color(15, 23, 42));
                g2.fillRect(0, 0, w, h);

                // Grid lines
                g2.setColor(new Color(51, 65, 85, 80));
                for (int y = 20; y < h - 20; y += 30) {
                    g2.drawLine(40, y, w - 20, y);
                }

                List<Double> points = service.get30DayRunwayCurve();
                if (points.isEmpty()) return;

                double max = points.get(0) * 1.05;
                int n = points.size();

                int[] xPoints = new int[n];
                int[] yPoints = new int[n];

                for (int i = 0; i < n; i++) {
                    xPoints[i] = 45 + (int) ((double) i / (n - 1) * (w - 75));
                    double val = points.get(i);
                    yPoints[i] = (h - 35) - (int) (val / max * (h - 60));
                }

                // Draw Area
                Polygon poly = new Polygon();
                poly.addPoint(xPoints[0], h - 35);
                for (int i = 0; i < n; i++) {
                    poly.addPoint(xPoints[i], yPoints[i]);
                }
                poly.addPoint(xPoints[n - 1], h - 35);

                g2.setPaint(new GradientPaint(0, 0, new Color(56, 189, 248, 80), 0, h, new Color(56, 189, 248, 0)));
                g2.fillPolygon(poly);

                // Draw Curve
                g2.setColor(new Color(56, 189, 248));
                g2.setStroke(new BasicStroke(2.5f));
                for (int i = 0; i < n - 1; i++) {
                    g2.drawLine(xPoints[i], yPoints[i], xPoints[i + 1], yPoints[i + 1]);
                }

                // Points & Labels
                g2.setColor(new Color(52, 211, 153));
                for (int i = 0; i < n; i += 6) {
                    g2.fillOval(xPoints[i] - 4, yPoints[i] - 4, 8, 8);
                    g2.drawString("D" + i, xPoints[i] - 8, h - 18);
                }
            }
        };
        chartPanel.setPreferredSize(new Dimension(300, 220));
        chartCard.add(chartPanel, BorderLayout.CENTER);

        JLabel chartFooter = new JLabel("• Baseline: $5,420 | Projected Day 30: $4,240 | Solvency: 100% Guaranteed");
        chartFooter.setFont(new Font("Segoe UI", Font.PLAIN, 10));
        chartFooter.setForeground(new Color(148, 163, 184));
        chartCard.add(chartFooter, BorderLayout.SOUTH);
        centerGrid.add(chartCard);

        // RIGHT: COMMAND TERMINAL & PROMPT CHIPS
        JPanel consoleCard = new JPanel(new BorderLayout(0, 8));
        consoleCard.setBackground(new Color(24, 30, 42));
        consoleCard.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createLineBorder(new Color(51, 65, 85)),
                BorderFactory.createEmptyBorder(10, 12, 10, 12)
        ));

        // Quick Prompt Chips
        JPanel chips = new JPanel(new FlowLayout(FlowLayout.LEFT, 6, 2));
        chips.setOpaque(false);
        chips.add(createPromptChip("🔍 Audit Student Budget", "audit student budget"));
        chips.add(createPromptChip("⚖️ Rebalance Portfolio", "rebalance portfolio"));
        chips.add(createPromptChip("📉 Check Cash Runway", "check cash runway"));
        chips.add(createPromptChip("💳 Simulate ₹65k EMI", "simulate 65000 emi"));
        consoleCard.add(chips, BorderLayout.NORTH);

        commandOutputArea = new JTextArea();
        commandOutputArea.setEditable(false);
        commandOutputArea.setFont(new Font("Consolas", Font.PLAIN, 11));
        commandOutputArea.setBackground(new Color(10, 15, 30));
        commandOutputArea.setForeground(new Color(0, 255, 200));
        commandOutputArea.setText("""
                [NEXUS QUANTITATIVE FINANCIAL CORE ONLINE]
                Autonomous agents initialized. 0 manual input needed.
                Click any suggestion chip above or enter an instruction below:
                --------------------------------------------------------------
                """);

        consoleCard.add(new JScrollPane(commandOutputArea), BorderLayout.CENTER);

        JPanel inputBar = new JPanel(new BorderLayout(6, 0));
        inputBar.setOpaque(false);
        commandInput = new JTextField();
        commandInput.setFont(new Font("Segoe UI", Font.PLAIN, 12));
        commandInput.addActionListener(e -> executeCommand(commandInput.getText().trim()));

        JButton runBtn = new JButton("Execute Agent ⚡");
        runBtn.setBackground(new Color(16, 185, 129));
        runBtn.setForeground(Color.WHITE);
        runBtn.setFont(new Font("Segoe UI", Font.BOLD, 11));
        runBtn.setFocusPainted(false);
        runBtn.addActionListener(e -> executeCommand(commandInput.getText().trim()));

        inputBar.add(commandInput, BorderLayout.CENTER);
        inputBar.add(runBtn, BorderLayout.EAST);
        consoleCard.add(inputBar, BorderLayout.SOUTH);

        centerGrid.add(consoleCard);
        add(centerGrid, BorderLayout.CENTER);

        // 3. BOTTOM HUD STRIP
        JPanel bottomBar = new JPanel(new FlowLayout(FlowLayout.LEFT, 18, 4));
        bottomBar.setBackground(new Color(30, 41, 59));
        bottomBar.setBorder(BorderFactory.createLineBorder(new Color(51, 65, 85)));

        JLabel balLabel = new JLabel("Standing Balance: $5,420.00");
        balLabel.setFont(new Font("Consolas", Font.BOLD, 12));
        balLabel.setForeground(Color.WHITE);

        JLabel burnLabel = new JLabel("Daily Burn Rate: $38.50");
        burnLabel.setFont(new Font("Consolas", Font.BOLD, 12));
        burnLabel.setForeground(new Color(251, 191, 36));

        JLabel limitLabel = new JLabel("Safe Daily Allowance: $65.00");
        limitLabel.setFont(new Font("Consolas", Font.BOLD, 12));
        limitLabel.setForeground(new Color(52, 211, 153));

        JLabel runwayLabel = new JLabel("Runway: 140 Days (~4.6 Months)");
        runwayLabel.setFont(new Font("Consolas", Font.BOLD, 12));
        runwayLabel.setForeground(new Color(56, 189, 248));

        bottomBar.add(balLabel);
        bottomBar.add(burnLabel);
        bottomBar.add(limitLabel);
        bottomBar.add(runwayLabel);
        add(bottomBar, BorderLayout.SOUTH);
    }

    private JButton createPromptChip(String title, String cmd) {
        JButton btn = new JButton(title);
        btn.setFont(new Font("Segoe UI", Font.PLAIN, 10));
        btn.setBackground(new Color(30, 41, 59));
        btn.setForeground(Color.WHITE);
        btn.setFocusPainted(false);
        btn.addActionListener(e -> {
            commandInput.setText(cmd);
            executeCommand(cmd);
        });
        return btn;
    }

    private void executeCommand(String cmd) {
        if (cmd.isEmpty()) return;
        commandInput.setText("");
        commandOutputArea.append("\n> " + cmd + "\n[Processing quantitative optimization heuristics...]\n");
        commandOutputArea.setCaretPosition(commandOutputArea.getDocument().getLength());

        new Thread(() -> {
            String response = service.executeNaturalLanguageCommand(cmd);
            SwingUtilities.invokeLater(() -> {
                commandOutputArea.append(response + "\n");
                commandOutputArea.setCaretPosition(commandOutputArea.getDocument().getLength());
            });
        }).start();
    }

    private void renderAgentCards() {
        agentsContainer.removeAll();
        for (CopilotAgentReport r : service.getAgentReports()) {
            JPanel card = new JPanel();
            card.setLayout(new BoxLayout(card, BoxLayout.Y_AXIS));
            card.setBackground(new Color(30, 41, 59));
            card.setBorder(BorderFactory.createCompoundBorder(
                    BorderFactory.createMatteBorder(0, 3, 0, 0, new Color(59, 130, 246)),
                    BorderFactory.createEmptyBorder(8, 10, 8, 10)
            ));

            JLabel title = new JLabel(r.getAgentName());
            title.setFont(new Font("Segoe UI", Font.BOLD, 11));
            title.setForeground(Color.WHITE);

            JLabel role = new JLabel(r.getRole() + " • " + r.getStatus());
            role.setFont(new Font("Consolas", Font.BOLD, 10));
            role.setForeground(new Color(52, 211, 153));

            JLabel insight = new JLabel("<html><body style='width:240px; color:#cbd5e1; font-size:9px;'>" + r.getInsight() + "</body></html>");

            JLabel action = new JLabel("<html><body style='width:240px; color:#38bdf8; font-size:9px;'>✓ " + r.getActionTaken() + "</body></html>");

            card.add(title);
            card.add(Box.createVerticalStrut(2));
            card.add(role);
            card.add(Box.createVerticalStrut(3));
            card.add(insight);
            card.add(Box.createVerticalStrut(3));
            card.add(action);

            agentsContainer.add(card);
        }
        agentsContainer.revalidate();
        agentsContainer.repaint();
    }
}