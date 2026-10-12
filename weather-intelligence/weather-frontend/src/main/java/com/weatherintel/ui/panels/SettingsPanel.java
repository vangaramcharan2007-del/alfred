package com.weatherintel.ui.panels;

import com.formdev.flatlaf.FlatDarkLaf;
import com.formdev.flatlaf.FlatLightLaf;
import com.weatherintel.ui.services.ApiClient;

import javax.swing.*;
import javax.swing.border.EmptyBorder;
import javax.swing.border.LineBorder;
import java.awt.*;
import java.util.prefs.Preferences;

/**
 * Settings and configuration panel for Weather Intelligence application.
 * Persists preferences using java.util.prefs.Preferences.
 * Manages unit conversions, auto-refresh frequency, API server URL, FlatLaf theme switching,
 * cache configuration, and application metadata.
 */
public class SettingsPanel extends JPanel {

    private static final Color BG_DARK = new Color(0x1E, 0x1E, 0x1E);
    private static final Color CARD_BG = new Color(0x2D, 0x2D, 0x2D);
    private static final Color PRIMARY_BLUE = new Color(0x1E, 0x3E, 0x72);
    private static final Color SECONDARY_BLUE = new Color(0x21, 0x96, 0xF3);
    private static final Color ACCENT_ORANGE = new Color(0xFF, 0x98, 0x00);
    private static final Color TEXT_MUTED = new Color(170, 175, 185);
    private static final Color BORDER_COLOR = new Color(60, 65, 75);

    // Preference keys
    private static final String PREF_TEMP_UNIT = "temp_unit";
    private static final String PREF_WIND_UNIT = "wind_unit";
    private static final String PREF_PRESSURE_UNIT = "pressure_unit";
    private static final String PREF_REFRESH_INTERVAL = "refresh_interval";
    private static final String PREF_BACKEND_URL = "backend_url";
    private static final String PREF_THEME = "ui_theme";
    private static final String PREF_CACHE_ENABLED = "cache_enabled";
    private static final String PREF_CACHE_TTL = "cache_ttl";

    private final Preferences prefs = Preferences.userNodeForPackage(SettingsPanel.class);
    private final ApiClient apiClient;

    // UI Input Components
    private final JComboBox<String> tempUnitCombo;
    private final JComboBox<String> windUnitCombo;
    private final JComboBox<String> pressureUnitCombo;
    private final JComboBox<Integer> refreshIntervalCombo;
    private final JTextField backendUrlField;
    private final JComboBox<String> themeCombo;
    private final JCheckBox cacheEnabledCheck;
    private final JSpinner cacheTtlSpinner;

    private final JButton applyButton;
    private final JButton resetButton;
    private final JLabel statusMessageLabel;

    public SettingsPanel(ApiClient apiClient) {
        this.apiClient = apiClient != null ? apiClient : new ApiClient();

        setLayout(new BorderLayout(15, 15));
        setBackground(BG_DARK);
        setBorder(new EmptyBorder(15, 15, 15, 15));

        // 1. TOP HEADER
        JPanel headerPanel = new JPanel(new BorderLayout());
        headerPanel.setOpaque(false);

        JLabel titleLabel = new JLabel("System Settings & Preferences");
        titleLabel.setFont(new Font("Segoe UI", Font.BOLD, 20));
        titleLabel.setForeground(Color.WHITE);

        JLabel subtitleLabel = new JLabel("Configure unit representations, network connections, caching, and theme.");
        subtitleLabel.setFont(new Font("Segoe UI", Font.PLAIN, 12));
        subtitleLabel.setForeground(TEXT_MUTED);

        headerPanel.add(titleLabel, BorderLayout.NORTH);
        headerPanel.add(subtitleLabel, BorderLayout.SOUTH);
        add(headerPanel, BorderLayout.NORTH);

        // 2. CENTER CONTENT (Split into Settings Groups)
        JPanel contentPanel = new JPanel(new GridBagLayout());
        contentPanel.setOpaque(false);

        GridBagConstraints gbc = new GridBagConstraints();
        gbc.fill = GridBagConstraints.HORIZONTAL;
        gbc.insets = new Insets(8, 8, 8, 8);
        gbc.weightx = 1.0;
        gbc.gridx = 0;
        gbc.gridy = 0;

        // Group 1: Units and Measurement
        JPanel unitsCard = createSectionCard("Units & Measurement");
        unitsCard.setLayout(new GridLayout(3, 2, 10, 8));

        unitsCard.add(createFormLabel("Temperature Unit:"));
        tempUnitCombo = new JComboBox<>(new String[]{"Celsius (°C)", "Fahrenheit (°F)"});
        unitsCard.add(styleCombo(tempUnitCombo));

        unitsCard.add(createFormLabel("Wind Speed Unit:"));
        windUnitCombo = new JComboBox<>(new String[]{"m/s", "km/h", "mph", "knots"});
        unitsCard.add(styleCombo(windUnitCombo));

        unitsCard.add(createFormLabel("Pressure Unit:"));
        pressureUnitCombo = new JComboBox<>(new String[]{"hPa", "mmHg"});
        unitsCard.add(styleCombo(pressureUnitCombo));

        contentPanel.add(unitsCard, gbc);

        // Group 2: Synchronization & Network
        gbc.gridy++;
        JPanel networkCard = createSectionCard("Network & Synchronization");
        networkCard.setLayout(new GridLayout(2, 2, 10, 8));

        networkCard.add(createFormLabel("Auto-Refresh Interval (minutes):"));
        refreshIntervalCombo = new JComboBox<>(new Integer[]{1, 2, 5, 10, 15, 30});
        networkCard.add(styleCombo(refreshIntervalCombo));

        networkCard.add(createFormLabel("Backend REST URL:"));
        backendUrlField = new JTextField();
        backendUrlField.setFont(new Font("Segoe UI", Font.PLAIN, 12));
        backendUrlField.setBackground(new Color(36, 40, 48));
        backendUrlField.setForeground(Color.WHITE);
        backendUrlField.setCaretColor(Color.WHITE);
        backendUrlField.setBorder(BorderFactory.createCompoundBorder(
                new LineBorder(BORDER_COLOR, 1, true),
                new EmptyBorder(4, 6, 4, 6)
        ));
        networkCard.add(backendUrlField);

        contentPanel.add(networkCard, gbc);

        // Group 3: Appearance & Theme
        gbc.gridy++;
        JPanel themeCard = createSectionCard("Appearance & Theme");
        themeCard.setLayout(new GridLayout(1, 2, 10, 8));

        themeCard.add(createFormLabel("Application Theme:"));
        themeCombo = new JComboBox<>(new String[]{"Dark (FlatLaf Dark)", "Light (FlatLaf Light)"});
        themeCard.add(styleCombo(themeCombo));

        contentPanel.add(themeCard, gbc);

        // Group 4: Cache Management
        gbc.gridy++;
        JPanel cacheCard = createSectionCard("Offline Cache Settings");
        cacheCard.setLayout(new GridLayout(2, 2, 10, 8));

        cacheCard.add(createFormLabel("Enable Local Caching:"));
        cacheEnabledCheck = new JCheckBox("Active", true);
        cacheEnabledCheck.setFont(new Font("Segoe UI", Font.PLAIN, 12));
        cacheEnabledCheck.setForeground(Color.WHITE);
        cacheEnabledCheck.setOpaque(false);
        cacheCard.add(cacheEnabledCheck);

        cacheCard.add(createFormLabel("Cache Expiry / TTL (minutes):"));
        cacheTtlSpinner = new JSpinner(new SpinnerNumberModel(30, 5, 1440, 5));
        cacheTtlSpinner.setFont(new Font("Segoe UI", Font.PLAIN, 12));
        cacheCard.add(cacheTtlSpinner);

        contentPanel.add(cacheCard, gbc);

        // Group 5: About & System Info
        gbc.gridy++;
        JPanel aboutCard = createSectionCard("About Weather Intelligence System");
        aboutCard.setLayout(new GridLayout(2, 1, 4, 4));

        JLabel versionLabel = new JLabel("Version: 1.0.0-PROD | Java 21 LTS | FlatLaf 3.4 | JFreeChart 1.5.4");
        versionLabel.setFont(new Font("Segoe UI", Font.PLAIN, 12));
        versionLabel.setForeground(TEXT_MUTED);

        JLabel descLabel = new JLabel("Enterprise-grade weather intelligence platform with OpenWeather API integration.");
        descLabel.setFont(new Font("Segoe UI", Font.ITALIC, 11));
        descLabel.setForeground(TEXT_MUTED);

        aboutCard.add(versionLabel);
        aboutCard.add(descLabel);

        contentPanel.add(aboutCard, gbc);

        JScrollPane scrollPane = new JScrollPane(contentPanel);
        scrollPane.setBorder(null);
        scrollPane.getViewport().setBackground(BG_DARK);
        scrollPane.getVerticalScrollBar().setUnitIncrement(16);

        add(scrollPane, BorderLayout.CENTER);

        // 3. BOTTOM ACTIONS
        JPanel bottomBar = new JPanel(new BorderLayout());
        bottomBar.setOpaque(false);
        bottomBar.setBorder(new EmptyBorder(10, 0, 0, 0));

        statusMessageLabel = new JLabel("");
        statusMessageLabel.setFont(new Font("Segoe UI", Font.PLAIN, 12));
        statusMessageLabel.setForeground(new Color(100, 220, 120));

        JPanel buttonsPanel = new JPanel(new FlowLayout(FlowLayout.RIGHT, 12, 0));
        buttonsPanel.setOpaque(false);

        resetButton = new JButton("Reset to Defaults");
        resetButton.setFont(new Font("Segoe UI", Font.PLAIN, 12));
        resetButton.setBackground(CARD_BG);
        resetButton.setForeground(Color.WHITE);
        resetButton.setFocusPainted(false);
        resetButton.addActionListener(e -> resetToDefaults());

        applyButton = new JButton("Apply Settings");
        applyButton.setFont(new Font("Segoe UI", Font.BOLD, 12));
        applyButton.setBackground(SECONDARY_BLUE);
        applyButton.setForeground(Color.WHITE);
        applyButton.setFocusPainted(false);
        applyButton.setCursor(new Cursor(Cursor.HAND_CURSOR));
        applyButton.addActionListener(e -> applySettings());

        buttonsPanel.add(resetButton);
        buttonsPanel.add(applyButton);

        bottomBar.add(statusMessageLabel, BorderLayout.WEST);
        bottomBar.add(buttonsPanel, BorderLayout.EAST);

        add(bottomBar, BorderLayout.SOUTH);

        // Load saved preferences into components
        loadPreferences();
    }

    private JPanel createSectionCard(String title) {
        JPanel card = new JPanel();
        card.setBackground(CARD_BG);
        card.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createTitledBorder(
                        new LineBorder(BORDER_COLOR, 1, true),
                        title,
                        0,
                        0,
                        new Font("Segoe UI", Font.BOLD, 12),
                        Color.WHITE
                ),
                new EmptyBorder(10, 14, 10, 14)
        ));
        return card;
    }

    private JLabel createFormLabel(String text) {
        JLabel label = new JLabel(text);
        label.setFont(new Font("Segoe UI", Font.PLAIN, 12));
        label.setForeground(Color.WHITE);
        return label;
    }

    private <T> JComboBox<T> styleCombo(JComboBox<T> combo) {
        combo.setFont(new Font("Segoe UI", Font.PLAIN, 12));
        combo.setBackground(new Color(36, 40, 48));
        combo.setForeground(Color.WHITE);
        return combo;
    }

    private void loadPreferences() {
        String tempUnit = prefs.get(PREF_TEMP_UNIT, "Celsius (°C)");
        tempUnitCombo.setSelectedItem(tempUnit);

        String windUnit = prefs.get(PREF_WIND_UNIT, "m/s");
        windUnitCombo.setSelectedItem(windUnit);

        String pressureUnit = prefs.get(PREF_PRESSURE_UNIT, "hPa");
        pressureUnitCombo.setSelectedItem(pressureUnit);

        int interval = prefs.getInt(PREF_REFRESH_INTERVAL, 5);
        refreshIntervalCombo.setSelectedItem(interval);

        String backendUrl = prefs.get(PREF_BACKEND_URL, apiClient != null ? apiClient.getBaseUrl() : "http://localhost:8080");
        backendUrlField.setText(backendUrl);

        String theme = prefs.get(PREF_THEME, "Dark (FlatLaf Dark)");
        themeCombo.setSelectedItem(theme);

        boolean cacheEnabled = prefs.getBoolean(PREF_CACHE_ENABLED, true);
        cacheEnabledCheck.setSelected(cacheEnabled);

        int ttl = prefs.getInt(PREF_CACHE_TTL, 30);
        cacheTtlSpinner.setValue(ttl);
    }

    public void applySettings() {
        try {
            // Save to Preferences
            prefs.put(PREF_TEMP_UNIT, (String) tempUnitCombo.getSelectedItem());
            prefs.put(PREF_WIND_UNIT, (String) windUnitCombo.getSelectedItem());
            prefs.put(PREF_PRESSURE_UNIT, (String) pressureUnitCombo.getSelectedItem());

            Integer interval = (Integer) refreshIntervalCombo.getSelectedItem();
            if (interval != null) {
                prefs.putInt(PREF_REFRESH_INTERVAL, interval);
            }

            String url = backendUrlField.getText().trim();
            if (!url.isEmpty()) {
                prefs.put(PREF_BACKEND_URL, url);
            }

            String selectedTheme = (String) themeCombo.getSelectedItem();
            prefs.put(PREF_THEME, selectedTheme);

            prefs.putBoolean(PREF_CACHE_ENABLED, cacheEnabledCheck.isSelected());
            prefs.putInt(PREF_CACHE_TTL, (Integer) cacheTtlSpinner.getValue());

            prefs.flush();

            // Switch Theme dynamically
            applyTheme(selectedTheme);

            statusMessageLabel.setText("✓ Settings successfully applied and saved.");
            Timer clearTimer = new Timer(3000, e -> statusMessageLabel.setText(""));
            clearTimer.setRepeats(false);
            clearTimer.start();
        } catch (Exception ex) {
            JOptionPane.showMessageDialog(this, "Failed to persist settings: " + ex.getMessage(), "Error", JOptionPane.ERROR_MESSAGE);
        }
    }

    public void resetToDefaults() {
        tempUnitCombo.setSelectedItem("Celsius (°C)");
        windUnitCombo.setSelectedItem("m/s");
        pressureUnitCombo.setSelectedItem("hPa");
        refreshIntervalCombo.setSelectedItem(5);
        backendUrlField.setText("http://localhost:8080");
        themeCombo.setSelectedItem("Dark (FlatLaf Dark)");
        cacheEnabledCheck.setSelected(true);
        cacheTtlSpinner.setValue(30);

        applySettings();
    }

    private void applyTheme(String themeName) {
        SwingUtilities.invokeLater(() -> {
            try {
                if (themeName != null && themeName.contains("Light")) {
                    FlatLightLaf.setup();
                } else {
                    FlatDarkLaf.setup();
                }
                Window window = SwingUtilities.getWindowAncestor(this);
                if (window != null) {
                    SwingUtilities.updateComponentTreeUI(window);
                }
            } catch (Exception ignored) {
            }
        });
    }

    public boolean isCelsius() {
        String unit = (String) tempUnitCombo.getSelectedItem();
        return unit == null || unit.contains("Celsius");
    }

    public String getWindSpeedUnit() {
        return (String) windUnitCombo.getSelectedItem();
    }

    public String getPressureUnit() {
        return (String) pressureUnitCombo.getSelectedItem();
    }

    public int getAutoRefreshIntervalMinutes() {
        Integer val = (Integer) refreshIntervalCombo.getSelectedItem();
        return val != null ? val : 5;
    }

    public String getBackendUrl() {
        return backendUrlField.getText().trim();
    }
}
