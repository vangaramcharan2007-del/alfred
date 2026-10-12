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
 * Supports authentication, user session display, multi-tab layout, and logout.
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
    private ApiClient.UserProfile currentUser;

    public WeatherApp() {
        this(new ApiClient.UserProfile(1L, "admin", "admin@weatherintel.com", "ADMIN", "System Administrator"), new ApiClient("http://localhost:8080"));
    }

    public WeatherApp(ApiClient.UserProfile userProfile) {
        this(userProfile, new ApiClient("http://localhost:8080"));
    }

    public WeatherApp(ApiClient.UserProfile userProfile, ApiClient client) {
        this.currentUser = (userProfile != null)
                ? userProfile
                : new ApiClient.UserProfile(1L, "admin", "admin@weatherintel.com", "ADMIN", "System Administrator");
        this.apiClient = (client != null) ? client : new ApiClient("http://localhost:8080");
        this.apiClient.setCurrentUser(this.currentUser);

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
        setTitle("Weather Intelligence & Monitoring System - [" + currentUser.getFullName() + "]");
        setDefaultCloseOperation(EXIT_ON_CLOSE);
        setSize(1400, 900);
        setMinimumSize(new Dimension(1200, 700));
        setLocationRelativeTo(null);

        // Create header with logo, search, and user profile
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
        header.setBackground(new Color(25, 45, 85));
        header.setBorder(BorderFactory.createEmptyBorder(10, 20, 10, 20));

        // Left Branding
        JPanel brandingPanel = new JPanel(new FlowLayout(FlowLayout.LEFT, 10, 0));
        brandingPanel.setOpaque(false);

        JLabel titleLabel = new JLabel("\u2601 Weather Intelligence");
        titleLabel.setFont(new Font("Segoe UI", Font.BOLD, 22));
        titleLabel.setForeground(Color.WHITE);
        brandingPanel.add(titleLabel);

        // Right Controls: Search + User Session Badge + Logout Button
        JPanel rightControls = new JPanel(new FlowLayout(FlowLayout.RIGHT, 12, 0));
        rightControls.setOpaque(false);

        // Search Field
        JTextField searchField = new JTextField(16);
        searchField.putClientProperty("JTextField.placeholderText", "Search city...");
        searchField.setFont(new Font("Segoe UI", Font.PLAIN, 13));

        JButton searchBtn = new JButton("Search");
        searchBtn.setFont(new Font("Segoe UI", Font.PLAIN, 12));
        searchBtn.addActionListener(e -> {
            String city = searchField.getText().trim();
            if (!city.isEmpty()) {
                dashboardPanel.loadWeather(city);
                tabbedPane.setSelectedIndex(0);
            }
        });
        searchField.addActionListener(e -> searchBtn.doClick());

        // User Badge
        JPanel userBadge = new JPanel(new FlowLayout(FlowLayout.LEFT, 6, 2));
        userBadge.setBackground(new Color(38, 55, 95));
        userBadge.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createLineBorder(new Color(65, 85, 135), 1, true),
                BorderFactory.createEmptyBorder(2, 8, 2, 8)
        ));

        JLabel userIcon = new JLabel("\uD83D\uDC64");
        userIcon.setFont(new Font("Segoe UI", Font.PLAIN, 13));

        JLabel userNameLabel = new JLabel(currentUser.getFullName() + " (" + currentUser.getRole() + ")");
        userNameLabel.setFont(new Font("Segoe UI", Font.BOLD, 12));
        userNameLabel.setForeground(new Color(220, 235, 255));

        userBadge.add(userIcon);
        userBadge.add(userNameLabel);

        // Logout Button
        JButton logoutBtn = new JButton("Logout");
        logoutBtn.setFont(new Font("Segoe UI", Font.PLAIN, 12));
        logoutBtn.setBackground(new Color(175, 45, 45));
        logoutBtn.setForeground(Color.WHITE);
        logoutBtn.setFocusPainted(false);
        logoutBtn.setCursor(new Cursor(Cursor.HAND_CURSOR));
        logoutBtn.addActionListener(e -> logout());

        rightControls.add(searchField);
        rightControls.add(searchBtn);
        rightControls.add(userBadge);
        rightControls.add(logoutBtn);

        header.add(brandingPanel, BorderLayout.WEST);
        header.add(rightControls, BorderLayout.EAST);
        return header;
    }

    public void logout() {
        int confirm = JOptionPane.showConfirmDialog(
                this,
                "Are you sure you want to log out?",
                "Confirm Logout",
                JOptionPane.YES_NO_OPTION,
                JOptionPane.QUESTION_MESSAGE
        );

        if (confirm != JOptionPane.YES_OPTION) {
            return;
        }

        dispose();
        if (webSocketClient != null) {
            try {
                webSocketClient.disconnect();
            } catch (Exception ignored) {
            }
        }

        SwingUtilities.invokeLater(() -> {
            LoginDialog loginDialog = new LoginDialog(null, apiClient);
            loginDialog.setVisible(true);
            if (loginDialog.isAuthenticated()) {
                WeatherApp newApp = new WeatherApp(loginDialog.getAuthenticatedUser(), apiClient);
                newApp.setVisible(true);
            }
        });
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

    public ApiClient.UserProfile getCurrentUser() {
        return currentUser;
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
            ApiClient client = new ApiClient();
            LoginDialog loginDialog = new LoginDialog(null, client);
            loginDialog.setVisible(true);

            if (loginDialog.isAuthenticated()) {
                WeatherApp app = new WeatherApp(loginDialog.getAuthenticatedUser(), client);
                app.setVisible(true);
            } else {
                System.exit(0);
            }
        });
    }
}
