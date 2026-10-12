package com.weatherintel.ui;

import com.formdev.flatlaf.FlatDarkLaf;
import com.weatherintel.ui.panels.*;
import com.weatherintel.ui.services.ApiClient;
import com.weatherintel.ui.services.WebSocketClient;

import javax.swing.*;
import java.awt.*;
import java.time.LocalDateTime;

/**
 * Main application window for Weather Intelligence & Monitoring System.
 */
public class WeatherApp extends JFrame {
    private JTabbedPane tabbedPane;
    private DashboardPanel dashboardPanel;
    private ForecastPanel forecastPanel;
    private MultiCityPanel multiCityPanel;
    private HistoricalPanel historicalPanel;
    private AlertsPanel alertsPanel;
    private SettingsPanel settingsPanel;
    private StatusBar statusBar;
    private ApiClient apiClient;
    private WebSocketClient webSocketClient;

    public WeatherApp() {
        apiClient = new ApiClient("http://localhost:8080");
        initUI();
        if (apiClient.isFallbackMode()) {
            if (statusBar != null) {
                statusBar.setConnected(true);
                statusBar.setServerUrl("In-Process Java Engine (Standalone Mode)");
                statusBar.setLastUpdated(LocalDateTime.now());
            }
        } else {
            initWebSocket();
        }
    }

    private void initUI() {
        setTitle("Weather Intelligence & Monitoring System");
        setDefaultCloseOperation(EXIT_ON_CLOSE);
        setSize(1400, 900);
        setMinimumSize(new Dimension(1200, 700));
        setLocationRelativeTo(null);

        // Create header with logo and search
        JPanel headerPanel = createHeaderPanel();

        // Create tabbed pane with custom styling
        tabbedPane = new JTabbedPane(JTabbedPane.LEFT);
        tabbedPane.setFont(new Font("Segoe UI", Font.PLAIN, 14));

        dashboardPanel = new DashboardPanel(apiClient);
        forecastPanel = new ForecastPanel(apiClient);
        multiCityPanel = new MultiCityPanel(apiClient);
        historicalPanel = new HistoricalPanel(apiClient);
        alertsPanel = new AlertsPanel(apiClient);
        settingsPanel = new SettingsPanel(apiClient);

        tabbedPane.addTab("  \u2600 Dashboard  ", dashboardPanel);
        tabbedPane.addTab("  \u26C5 Forecast  ", forecastPanel);
        tabbedPane.addTab("  \u2637 Cities  ", multiCityPanel);
        tabbedPane.addTab("  \u2616 History  ", historicalPanel);
        tabbedPane.addTab("  \u26A0 Alerts  ", alertsPanel);
        tabbedPane.addTab("  \u2699 Settings  ", settingsPanel);

        statusBar = new StatusBar(apiClient.getBaseUrl());
        if (apiClient.isFallbackMode()) {
            statusBar.setConnected(true);
            statusBar.setLastUpdated(LocalDateTime.now());
        }

        setLayout(new BorderLayout());
        add(headerPanel, BorderLayout.NORTH);
        add(tabbedPane, BorderLayout.CENTER);
        add(statusBar, BorderLayout.SOUTH);
    }

    private void initWebSocket() {
        try {
            webSocketClient = new WebSocketClient("ws://localhost:8080/ws");
            webSocketClient.addConnectionStatusListener(connected -> {
                if (statusBar != null) {
                    statusBar.setConnected(connected);
                }
            });
            webSocketClient.addWeatherUpdateListener(data -> {
                if (statusBar != null) {
                    statusBar.setLastUpdated(LocalDateTime.now());
                }
            });
            webSocketClient.connect();
        } catch (Exception e) {
            // Silently handle initial websocket connection failure; auto-reconnect will retry
        }
    }

    private JPanel createHeaderPanel() {
        JPanel header = new JPanel(new BorderLayout());
        header.setBackground(new Color(30, 60, 114));
        header.setBorder(BorderFactory.createEmptyBorder(10, 20, 10, 20));

        JLabel titleLabel = new JLabel("\u2601 Weather Intelligence");
        titleLabel.setFont(new Font("Segoe UI", Font.BOLD, 22));
        titleLabel.setForeground(Color.WHITE);

        // Search panel
        JPanel searchPanel = new JPanel(new FlowLayout(FlowLayout.RIGHT));
        searchPanel.setOpaque(false);
        JTextField searchField = new JTextField(20);
        searchField.putClientProperty("JTextField.placeholderText", "Search city...");
        JButton searchBtn = new JButton("Search");
        searchBtn.addActionListener(e -> {
            String city = searchField.getText().trim();
            if (!city.isEmpty()) {
                dashboardPanel.loadWeather(city);
                tabbedPane.setSelectedIndex(0);
            }
        });
        searchField.addActionListener(e -> searchBtn.doClick());
        searchPanel.add(searchField);
        searchPanel.add(searchBtn);

        header.add(titleLabel, BorderLayout.WEST);
        header.add(searchPanel, BorderLayout.EAST);
        return header;
    }

    public JTabbedPane getTabbedPane() {
        return tabbedPane;
    }

    public DashboardPanel getDashboardPanel() {
        return dashboardPanel;
    }

    public ForecastPanel getForecastPanel() {
        return forecastPanel;
    }

    public MultiCityPanel getMultiCityPanel() {
        return multiCityPanel;
    }

    public HistoricalPanel getHistoricalPanel() {
        return historicalPanel;
    }

    public AlertsPanel getAlertsPanel() {
        return alertsPanel;
    }

    public SettingsPanel getSettingsPanel() {
        return settingsPanel;
    }

    public StatusBar getStatusBar() {
        return statusBar;
    }

    public ApiClient getApiClient() {
        return apiClient;
    }

    public WebSocketClient getWebSocketClient() {
        return webSocketClient;
    }

    public static void main(String[] args) {
        try {
            UIManager.setLookAndFeel(new FlatDarkLaf());
        } catch (Exception e) {
            try {
                UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName());
            } catch (Exception ignored) {
            }
        }
        SwingUtilities.invokeLater(() -> {
            WeatherApp app = new WeatherApp();
            app.setVisible(true);
        });
    }
}
