package nexus.dashboard;

import javax.swing.*;
import java.awt.*;
import java.util.Map;
import nexus.common.EventBus;
import nexus.common.NexusEvent;
import nexus.common.NexusListener;
import nexus.realtime.SRMWeatherService;

public class DashboardPanel extends JPanel implements NexusListener {
    private final DashboardService service;
    private final HudWidget scoreWidget;
    private final HudWidget budgetWidget;
    private final HudWidget tasksWidget;
    private final HudWidget goalsWidget;
    private final HudWidget mediaWidget;
    private final JLabel weatherLabel;
    
    public DashboardPanel(DashboardService service) {
        this.service = service;
        setLayout(new BorderLayout(15, 12));
        setBorder(BorderFactory.createEmptyBorder(15, 15, 15, 15));
        setBackground(new Color(15, 15, 20));

        // 1. TOP SRM CAMPUS LIVE TELEMETRY BANNER
        JPanel topBanner = new JPanel(new BorderLayout(10, 0));
        topBanner.setBackground(new Color(24, 30, 42));
        topBanner.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createLineBorder(new Color(51, 65, 85), 1),
                BorderFactory.createEmptyBorder(8, 14, 8, 14)
        ));

        JLabel telemetryTag = new JLabel("● LIVE CAMPUS TELEMETRY:");
        telemetryTag.setFont(new Font("Segoe UI", Font.BOLD, 11));
        telemetryTag.setForeground(new Color(52, 211, 153));

        weatherLabel = new JLabel("Connecting to SRM Kattankulathur atmospheric sensors...");
        weatherLabel.setFont(new Font("Consolas", Font.PLAIN, 12));
        weatherLabel.setForeground(new Color(224, 231, 255));

        JButton refreshWeatherBtn = new JButton("🔄 Sensor Sync");
        refreshWeatherBtn.setFont(new Font("Segoe UI", Font.BOLD, 11));
        refreshWeatherBtn.setBackground(new Color(59, 130, 246));
        refreshWeatherBtn.setForeground(Color.WHITE);
        refreshWeatherBtn.setFocusPainted(false);
        refreshWeatherBtn.setCursor(new Cursor(Cursor.HAND_CURSOR));
        refreshWeatherBtn.addActionListener(e -> fetchWeatherAsync());

        topBanner.add(telemetryTag, BorderLayout.WEST);
        topBanner.add(weatherLabel, BorderLayout.CENTER);
        topBanner.add(refreshWeatherBtn, BorderLayout.EAST);
        add(topBanner, BorderLayout.NORTH);

        // 2. CENTER NEURAL VISUALIZER
        NeuralVisualizerPanel visualizerPanel = new NeuralVisualizerPanel();
        visualizerPanel.setPreferredSize(new Dimension(800, 400));
        add(visualizerPanel, BorderLayout.CENTER);

        // 3. BOTTOM STATS HUD
        JPanel statsPanel = new JPanel(new GridLayout(1, 5, 12, 12));
        statsPanel.setOpaque(false);
        
        scoreWidget = new HudWidget("XP", "100", new Color(0, 255, 100));
        budgetWidget = new HudWidget("BUDGET", "0.00", new Color(0, 200, 255));
        tasksWidget = new HudWidget("TASKS", "0/0", new Color(255, 150, 0));
        goalsWidget = new HudWidget("GOALS", "0/0", new Color(200, 0, 255));
        mediaWidget = new HudWidget("WATCHLIST", "0", new Color(255, 50, 100));

        statsPanel.add(scoreWidget);
        statsPanel.add(budgetWidget);
        statsPanel.add(tasksWidget);
        statsPanel.add(goalsWidget);
        statsPanel.add(mediaWidget);
        
        add(statsPanel, BorderLayout.SOUTH);
        
        EventBus.getInstance().subscribe("DASHBOARD_UPDATED", this);
        updateView(service.getSummaryData());

        // Fetch weather asynchronously on startup
        fetchWeatherAsync();
    }

    private void fetchWeatherAsync() {
        weatherLabel.setText("Connecting to SRM Kattankulathur weather station...");
        new Thread(() -> {
            SRMWeatherService.WeatherData data = SRMWeatherService.fetchLiveWeather();
            SwingUtilities.invokeLater(() -> {
                weatherLabel.setText(data.toString());
            });
        }).start();
    }
    
    private void updateView(Map<String, Object> data) {
        scoreWidget.setValue(String.valueOf(data.get("XP")));
        budgetWidget.setValue(String.format("$%,.2f", (Double) data.getOrDefault("budget_remaining", 10000.0)));
        tasksWidget.setValue(data.getOrDefault("tasks_completed", 0) + "/" + data.getOrDefault("tasks_total", 0));
        goalsWidget.setValue(data.getOrDefault("goals_completed", 0) + "/" + data.getOrDefault("goals_total", 0));
        mediaWidget.setValue(String.valueOf(data.getOrDefault("media_total", 0)));
    }

    @Override
    public void onEvent(NexusEvent event) {
        if ("DASHBOARD_UPDATED".equals(event.getType())) {
            SwingUtilities.invokeLater(() -> {
                @SuppressWarnings("unchecked")
                Map<String, Object> data = (Map<String, Object>) event.getPayload();
                updateView(data);
            });
        }
    }

    // Glowing HUD widget
    private static class HudWidget extends JPanel {
        private final String title;
        private String value;
        private final Color glowColor;

        public HudWidget(String title, String value, Color glowColor) {
            this.title = title;
            this.value = value;
            this.glowColor = glowColor;
            setOpaque(false);
            setPreferredSize(new Dimension(150, 75));
        }

        public void setValue(String value) {
            this.value = value;
            repaint();
        }

        @Override
        protected void paintComponent(Graphics g) {
            super.paintComponent(g);
            Graphics2D g2 = (Graphics2D) g;
            g2.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);

            int w = getWidth();
            int h = getHeight();

            // Background glow
            g2.setColor(new Color(glowColor.getRed(), glowColor.getGreen(), glowColor.getBlue(), 28));
            g2.fillRoundRect(4, 4, w - 8, h - 8, 14, 14);

            // Border
            g2.setColor(new Color(glowColor.getRed(), glowColor.getGreen(), glowColor.getBlue(), 140));
            g2.setStroke(new BasicStroke(1.8f));
            g2.drawRoundRect(4, 4, w - 8, h - 8, 14, 14);

            // Title
            g2.setColor(new Color(200, 200, 220));
            g2.setFont(new Font("Consolas", Font.BOLD, 12));
            FontMetrics fmTitle = g2.getFontMetrics();
            int titleX = (w - fmTitle.stringWidth(title)) / 2;
            g2.drawString(title, titleX, 24);

            // Value
            g2.setColor(Color.WHITE);
            g2.setFont(new Font("Consolas", Font.BOLD, 20));
            FontMetrics fmValue = g2.getFontMetrics();
            int valueX = (w - fmValue.stringWidth(value)) / 2;
            g2.drawString(value, valueX, 52);

            // Corner accents
            g2.setColor(glowColor);
            g2.drawLine(4, 12, 4, 4);
            g2.drawLine(4, 4, 12, 4);
            g2.drawLine(w - 4, 12, w - 4, 4);
            g2.drawLine(w - 12, 4, w - 4, 4);
            g2.drawLine(4, h - 12, 4, h - 4);
            g2.drawLine(4, h - 4, 12, h - 4);
            g2.drawLine(w - 4, h - 12, w - 4, h - 4);
            g2.drawLine(w - 12, h - 4, w - 4, h - 4);
        }
    }
}
