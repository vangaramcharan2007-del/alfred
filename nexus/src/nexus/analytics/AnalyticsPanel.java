package nexus.analytics;

import javax.swing.*;
import java.awt.*;
import java.text.SimpleDateFormat;
import java.util.*;
import java.util.List;
import nexus.common.EventBus;
import nexus.common.NexusEvent;
import nexus.common.NexusListener;
import nexus.finance.Budget;

public class AnalyticsPanel extends JPanel implements NexusListener {
    private final AnalyticsService service;
    private final SimpleDateFormat timeFormat = new SimpleDateFormat("HH:mm:ss");

    // KPI Cards
    private JLabel xpLabel;
    private JLabel efficiencyLabel;
    private JLabel velocityLabel;
    private JLabel riskLabel;

    // Charts
    private final AnimatedBarChart barChart;
    private final PieChartPanel pieChart;
    private final Map<String, Double> barChartData = new LinkedHashMap<>();

    // Insights Stream
    private final JPanel insightsContainer;

    public AnalyticsPanel(AnalyticsService service) {
        this.service = service;
        setLayout(new BorderLayout(15, 12));
        setBorder(BorderFactory.createEmptyBorder(12, 12, 12, 12));
        setBackground(new Color(15, 23, 42));

        // 1. TOP EXECUTIVE INTELLIGENCE RIBBON (4 HUD CARDS)
        JPanel topRibbon = new JPanel(new GridLayout(1, 4, 10, 0));
        topRibbon.setOpaque(false);

        xpLabel = new JLabel("350 XP (Tier 4)");
        efficiencyLabel = new JLabel("88.5% Preserved");
        velocityLabel = new JLabel("92.4% Optimal");
        riskLabel = new JLabel("LOW (280d Runway)");

        topRibbon.add(createHudCard("COGNITIVE XP LEVEL", xpLabel, new Color(168, 85, 247)));
        topRibbon.add(createHudCard("FINANCIAL EFFICIENCY", efficiencyLabel, new Color(16, 185, 129)));
        topRibbon.add(createHudCard("TASK VELOCITY INDEX", velocityLabel, new Color(59, 130, 246)));
        topRibbon.add(createHudCard("SYSTEM RISK RATING", riskLabel, new Color(52, 211, 153)));

        add(topRibbon, BorderLayout.NORTH);

        // 2. CENTER SECTION (Dual Charts: Left Animated Bar Chart | Right Category Pie Chart)
        JPanel chartsGrid = new JPanel(new GridLayout(1, 2, 12, 0));
        chartsGrid.setOpaque(false);

        // Bar Chart
        barChart = new AnimatedBarChart();
        barChart.setBorder(BorderFactory.createTitledBorder(
                BorderFactory.createLineBorder(new Color(51, 65, 85)),
                "COMPARATIVE RESOURCE VELOCITY & CAPITAL FLOWS",
                0, 0, new Font("Segoe UI", Font.BOLD, 12), Color.CYAN));

        barChartData.put("Working Capital", 10000.0);
        barChartData.put("Liquid Reserves", 8450.0);
        barChartData.put("Total Expenses", 1550.0);
        barChartData.put("Passive Yield", 631.5);
        barChartData.put("Productivity XP", (double) service.getCurrentScore());
        barChart.setData(barChartData);

        chartsGrid.add(barChart);

        // Pie Chart
        pieChart = new PieChartPanel();
        pieChart.setBorder(BorderFactory.createTitledBorder(
                BorderFactory.createLineBorder(new Color(51, 65, 85)),
                "PORTFOLIO & EXPENSE ALLOCATION BREAKDOWN",
                0, 0, new Font("Segoe UI", Font.BOLD, 12), new Color(147, 197, 253)));

        Map<String, Double> samplePie = new LinkedHashMap<>();
        samplePie.put("Academics", 350.0);
        samplePie.put("Food & Canteen", 220.0);
        samplePie.put("Entertainment & Cinema", 525.0);
        samplePie.put("Amazon Shopping", 455.0);
        pieChart.setData(samplePie);

        chartsGrid.add(pieChart);

        // 3. BOTTOM SECTION: PREDICTIVE ANOMALY & INSIGHTS FEED
        JPanel bottomSection = new JPanel(new BorderLayout(8, 6));
        bottomSection.setBackground(new Color(24, 30, 42));
        bottomSection.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createLineBorder(new Color(51, 65, 85)),
                BorderFactory.createEmptyBorder(8, 12, 8, 12)
        ));
        bottomSection.setPreferredSize(new Dimension(800, 220));

        // Header + Run Diagnostics button
        JPanel headerBar = new JPanel(new BorderLayout(10, 0));
        headerBar.setOpaque(false);

        JLabel feedTitle = new JLabel("📊 AUTOMATED PREDICTIVE ANOMALY DETECTION & AUDIT STREAM");
        feedTitle.setFont(new Font("Segoe UI", Font.BOLD, 12));
        feedTitle.setForeground(new Color(56, 189, 248));

        JButton diagBtn = new JButton("⚡ Run System Diagnostics");
        diagBtn.setFont(new Font("Segoe UI", Font.BOLD, 11));
        diagBtn.setBackground(new Color(59, 130, 246));
        diagBtn.setForeground(Color.WHITE);
        diagBtn.setFocusPainted(false);
        diagBtn.setCursor(new Cursor(Cursor.HAND_CURSOR));
        diagBtn.addActionListener(e -> service.runFullDiagnostics());

        headerBar.add(feedTitle, BorderLayout.WEST);
        headerBar.add(diagBtn, BorderLayout.EAST);
        bottomSection.add(headerBar, BorderLayout.NORTH);

        // Insights Stream
        insightsContainer = new JPanel();
        insightsContainer.setLayout(new BoxLayout(insightsContainer, BoxLayout.Y_AXIS));
        insightsContainer.setBackground(new Color(24, 30, 42));

        JScrollPane scroll = new JScrollPane(insightsContainer);
        scroll.setBorder(BorderFactory.createEmptyBorder());
        scroll.getVerticalScrollBar().setUnitIncrement(14);
        bottomSection.add(scroll, BorderLayout.CENTER);

        // Assemble main layout
        JPanel centerContainer = new JPanel(new BorderLayout(0, 10));
        centerContainer.setOpaque(false);
        centerContainer.add(chartsGrid, BorderLayout.CENTER);
        centerContainer.add(bottomSection, BorderLayout.SOUTH);

        add(centerContainer, BorderLayout.CENTER);

        // EventBus Subscriptions
        EventBus.getInstance().subscribe("XP_UPDATED", this);
        EventBus.getInstance().subscribe("INSIGHT_GENERATED", this);
        EventBus.getInstance().subscribe("BUDGET_UPDATED", this);
        EventBus.getInstance().subscribe("TRANSACTION_ADDED", this);

        renderInsights(service.getInsights());
    }

    private JPanel createHudCard(String title, JLabel valueLabel, Color accent) {
        JPanel card = new JPanel(new BorderLayout(3, 3));
        card.setBackground(new Color(30, 41, 59));
        card.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createMatteBorder(0, 4, 0, 0, accent),
                BorderFactory.createEmptyBorder(8, 12, 8, 12)
        ));

        JLabel titleLabel = new JLabel(title);
        titleLabel.setFont(new Font("Segoe UI", Font.BOLD, 10));
        titleLabel.setForeground(new Color(156, 163, 175));

        valueLabel.setFont(new Font("Segoe UI", Font.BOLD, 15));
        valueLabel.setForeground(Color.WHITE);

        card.add(titleLabel, BorderLayout.NORTH);
        card.add(valueLabel, BorderLayout.CENTER);
        return card;
    }

    private void renderInsights(List<Insight> insights) {
        insightsContainer.removeAll();
        for (Insight i : insights) {
            JPanel card = new JPanel(new BorderLayout(8, 0));
            card.setBackground(new Color(30, 41, 59));
            card.setBorder(BorderFactory.createCompoundBorder(
                    BorderFactory.createMatteBorder(0, 3, 0, 0, i.getLevel().color),
                    BorderFactory.createEmptyBorder(6, 10, 6, 10)
            ));
            card.setMaximumSize(new Dimension(2000, 36));

            JLabel tag = new JLabel("[" + i.getLevel().label + "]");
            tag.setFont(new Font("Segoe UI", Font.BOLD, 10));
            tag.setForeground(i.getLevel().color);
            tag.setPreferredSize(new Dimension(95, 20));

            JLabel msg = new JLabel(i.getMessage());
            msg.setFont(new Font("Segoe UI", Font.PLAIN, 12));
            msg.setForeground(Color.WHITE);

            JLabel time = new JLabel(timeFormat.format(i.getTimestamp()));
            time.setFont(new Font("Consolas", Font.PLAIN, 11));
            time.setForeground(new Color(148, 163, 184));

            card.add(tag, BorderLayout.WEST);
            card.add(msg, BorderLayout.CENTER);
            card.add(time, BorderLayout.EAST);

            insightsContainer.add(card);
            insightsContainer.add(Box.createVerticalStrut(4));
        }
        insightsContainer.revalidate();
        insightsContainer.repaint();
    }

    @Override
    public void onEvent(NexusEvent event) {
        SwingUtilities.invokeLater(() -> {
            if ("XP_UPDATED".equals(event.getType())) {
                Object payload = event.getPayload();
                int scoreVal = payload instanceof Integer ? (Integer) payload : 100;
                xpLabel.setText(scoreVal + " XP (Tier " + (scoreVal / 100 + 1) + ")");
                barChartData.put("Productivity XP", (double) scoreVal);
                barChart.setData(barChartData);
            } else if ("BUDGET_UPDATED".equals(event.getType())) {
                Object payload = event.getPayload();
                if (payload instanceof Budget) {
                    Budget b = (Budget) payload;
                    barChartData.put("Working Capital", b.getTotalBudget());
                    barChartData.put("Liquid Reserves", Math.max(0, b.getRemaining()));
                    barChartData.put("Total Expenses", b.getCurrentSpent());
                    barChart.setData(barChartData);

                    double ratio = b.getTotalBudget() > 0 ? (b.getRemaining() / b.getTotalBudget()) * 100 : 0;
                    efficiencyLabel.setText(String.format("%.1f%% Preserved", ratio));
                }
            } else if ("INSIGHT_GENERATED".equals(event.getType())) {
                @SuppressWarnings("unchecked")
                List<Insight> updated = (List<Insight>) event.getPayload();
                renderInsights(updated);
            }
        });
    }
}
