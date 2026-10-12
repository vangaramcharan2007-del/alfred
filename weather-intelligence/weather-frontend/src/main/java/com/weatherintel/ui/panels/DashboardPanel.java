package com.weatherintel.ui.panels;

import com.weatherintel.ui.services.ApiClient;
import com.weatherintel.ui.services.ApiClient.WeatherData;
import com.weatherintel.ui.services.UnitConverter;

import javax.swing.*;
import javax.swing.border.EmptyBorder;
import javax.swing.border.LineBorder;
import java.awt.*;
import java.awt.event.ActionListener;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.concurrent.ExecutionException;

/**
 * Main weather dashboard panel displaying real-time weather metrics,
 * detailed condition cards, unit toggles, and auto-refresh controls.
 */
public class DashboardPanel extends JPanel {

    private static final Color BG_DARK = new Color(0x1E, 0x1E, 0x1E);
    private static final Color CARD_BG = new Color(0x2D, 0x2D, 0x2D);
    private static final Color PRIMARY_BLUE = new Color(0x1E, 0x3E, 0x72);
    private static final Color SECONDARY_BLUE = new Color(0x21, 0x96, 0xF3);
    private static final Color ACCENT_ORANGE = new Color(0xFF, 0x98, 0x00);
    private static final Color TEXT_MUTED = new Color(170, 175, 185);
    private static final Color BORDER_COLOR = new Color(60, 65, 75);

    private static final DateTimeFormatter TIME_FORMATTER = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

    private final ApiClient apiClient;

    // Header components
    private final JLabel cityCountryLabel;
    private final JLabel lastUpdatedLabel;
    private final JLabel dataSourceBadge;
    private final JButton refreshButton;
    private final JProgressBar progressBar;

    // Center main weather display
    private final JLabel tempLabel;
    private final JLabel conditionLabel;
    private final JLabel feelsLikeLabel;
    private final JLabel minMaxLabel;
    private final JLabel weatherIconLabel;

    // Detail cards
    private final JLabel humidityValLabel;
    private final JProgressBar humidityBar;
    private final JLabel pressureValLabel;
    private final JLabel windValLabel;
    private final JLabel visibilityValLabel;
    private final JLabel cloudsValLabel;
    private final JLabel sunriseSunsetValLabel;

    // Bottom controls
    private final JToggleButton unitToggle; // C / F
    private final JCheckBox autoRefreshCheck;
    private final JComboBox<Integer> intervalCombo;
    private final Timer autoRefreshTimer;

    // State
    private String currentCity = "London";
    private WeatherData currentWeatherData = null;
    private WeatherData cachedWeatherData = null;
    private boolean isCelsius = true;

    public DashboardPanel(ApiClient apiClient) {
        this.apiClient = apiClient != null ? apiClient : new ApiClient();

        setLayout(new BorderLayout(15, 15));
        setBackground(BG_DARK);
        setBorder(new EmptyBorder(15, 15, 15, 15));

        // 1. TOP HEADER PANEL
        JPanel topHeaderPanel = new JPanel(new BorderLayout(10, 10));
        topHeaderPanel.setOpaque(false);

        JPanel topLeftPanel = new JPanel();
        topLeftPanel.setLayout(new BoxLayout(topLeftPanel, BoxLayout.Y_AXIS));
        topLeftPanel.setOpaque(false);

        cityCountryLabel = new JLabel("Loading weather...");
        cityCountryLabel.setFont(new Font("Segoe UI", Font.BOLD, 24));
        cityCountryLabel.setForeground(Color.WHITE);

        JPanel subTitleRow = new JPanel(new FlowLayout(FlowLayout.LEFT, 10, 0));
        subTitleRow.setOpaque(false);

        lastUpdatedLabel = new JLabel("Last updated: --");
        lastUpdatedLabel.setFont(new Font("Segoe UI", Font.PLAIN, 12));
        lastUpdatedLabel.setForeground(TEXT_MUTED);

        dataSourceBadge = new JLabel(" API ");
        dataSourceBadge.setFont(new Font("Segoe UI", Font.BOLD, 11));
        dataSourceBadge.setOpaque(true);
        dataSourceBadge.setBackground(PRIMARY_BLUE);
        dataSourceBadge.setForeground(Color.WHITE);
        dataSourceBadge.setBorder(BorderFactory.createCompoundBorder(
                new LineBorder(SECONDARY_BLUE, 1, true),
                new EmptyBorder(2, 6, 2, 6)
        ));

        subTitleRow.add(lastUpdatedLabel);
        subTitleRow.add(dataSourceBadge);

        topLeftPanel.add(cityCountryLabel);
        topLeftPanel.add(Box.createVerticalStrut(4));
        topLeftPanel.add(subTitleRow);

        JPanel topRightPanel = new JPanel(new FlowLayout(FlowLayout.RIGHT, 10, 0));
        topRightPanel.setOpaque(false);

        refreshButton = new JButton("↻ Refresh");
        refreshButton.setFont(new Font("Segoe UI", Font.BOLD, 13));
        refreshButton.setBackground(SECONDARY_BLUE);
        refreshButton.setForeground(Color.WHITE);
        refreshButton.setFocusPainted(false);
        refreshButton.setCursor(new Cursor(Cursor.HAND_CURSOR));
        refreshButton.addActionListener(e -> loadWeather(currentCity));

        topRightPanel.add(refreshButton);

        topHeaderPanel.add(topLeftPanel, BorderLayout.WEST);
        topHeaderPanel.add(topRightPanel, BorderLayout.EAST);

        // Progress bar for async loading
        progressBar = new JProgressBar();
        progressBar.setIndeterminate(true);
        progressBar.setVisible(false);
        progressBar.setPreferredSize(new Dimension(100, 4));
        progressBar.setForeground(SECONDARY_BLUE);
        progressBar.setBackground(BG_DARK);

        JPanel headerContainer = new JPanel(new BorderLayout());
        headerContainer.setOpaque(false);
        headerContainer.add(topHeaderPanel, BorderLayout.CENTER);
        headerContainer.add(progressBar, BorderLayout.SOUTH);

        add(headerContainer, BorderLayout.NORTH);

        // 2. CENTER CONTENT (Split into left main display and right card grid)
        JPanel centerContainer = new JPanel(new GridBagLayout());
        centerContainer.setOpaque(false);

        GridBagConstraints gbc = new GridBagConstraints();
        gbc.fill = GridBagConstraints.BOTH;
        gbc.insets = new Insets(0, 0, 0, 15);
        gbc.weightx = 0.45;
        gbc.weighty = 1.0;
        gbc.gridx = 0;
        gbc.gridy = 0;

        // Big Main Temperature Card
        JPanel mainWeatherCard = createCardPanel();
        mainWeatherCard.setLayout(new GridBagLayout());
        GridBagConstraints mainGbc = new GridBagConstraints();
        mainGbc.gridx = 0;
        mainGbc.gridy = 0;
        mainGbc.anchor = GridBagConstraints.CENTER;
        mainGbc.insets = new Insets(8, 8, 8, 8);

        weatherIconLabel = new JLabel("☀️");
        weatherIconLabel.setFont(new Font("Segoe UI Emoji", Font.PLAIN, 64));
        weatherIconLabel.setForeground(ACCENT_ORANGE);
        mainWeatherCard.add(weatherIconLabel, mainGbc);

        mainGbc.gridy++;
        tempLabel = new JLabel("--°C");
        tempLabel.setFont(new Font("Segoe UI", Font.BOLD, 58));
        tempLabel.setForeground(Color.WHITE);
        mainWeatherCard.add(tempLabel, mainGbc);

        mainGbc.gridy++;
        conditionLabel = new JLabel("Clear Sky");
        conditionLabel.setFont(new Font("Segoe UI", Font.PLAIN, 20));
        conditionLabel.setForeground(new Color(220, 225, 235));
        mainWeatherCard.add(conditionLabel, mainGbc);

        mainGbc.gridy++;
        feelsLikeLabel = new JLabel("Feels like: --°C");
        feelsLikeLabel.setFont(new Font("Segoe UI", Font.PLAIN, 15));
        feelsLikeLabel.setForeground(TEXT_MUTED);
        mainWeatherCard.add(feelsLikeLabel, mainGbc);

        mainGbc.gridy++;
        minMaxLabel = new JLabel("Min: --°C  •  Max: --°C");
        minMaxLabel.setFont(new Font("Segoe UI", Font.PLAIN, 14));
        minMaxLabel.setForeground(TEXT_MUTED);
        mainWeatherCard.add(minMaxLabel, mainGbc);

        centerContainer.add(mainWeatherCard, gbc);

        // Right side: Detail Cards (2 Columns x 3 Rows)
        JPanel detailGrid = new JPanel(new GridLayout(3, 2, 12, 12));
        detailGrid.setOpaque(false);

        // Card 1: Humidity
        humidityValLabel = new JLabel("-- %");
        humidityValLabel.setFont(new Font("Segoe UI", Font.BOLD, 22));
        humidityValLabel.setForeground(Color.WHITE);
        humidityBar = new JProgressBar(0, 100);
        humidityBar.setValue(0);
        humidityBar.setStringPainted(true);
        humidityBar.setForeground(SECONDARY_BLUE);
        humidityBar.setBackground(new Color(40, 45, 55));
        detailGrid.add(createDetailCard("💧 Humidity", humidityValLabel, humidityBar));

        // Card 2: Pressure
        pressureValLabel = new JLabel("-- hPa");
        pressureValLabel.setFont(new Font("Segoe UI", Font.BOLD, 22));
        pressureValLabel.setForeground(Color.WHITE);
        detailGrid.add(createDetailCard("⏲ Pressure", pressureValLabel, null));

        // Card 3: Wind
        windValLabel = new JLabel("-- m/s (N)");
        windValLabel.setFont(new Font("Segoe UI", Font.BOLD, 22));
        windValLabel.setForeground(Color.WHITE);
        detailGrid.add(createDetailCard("💨 Wind Speed & Dir", windValLabel, null));

        // Card 4: Visibility
        visibilityValLabel = new JLabel("-- km");
        visibilityValLabel.setFont(new Font("Segoe UI", Font.BOLD, 22));
        visibilityValLabel.setForeground(Color.WHITE);
        detailGrid.add(createDetailCard("👁 Visibility", visibilityValLabel, null));

        // Card 5: Cloud cover
        cloudsValLabel = new JLabel("-- %");
        cloudsValLabel.setFont(new Font("Segoe UI", Font.BOLD, 22));
        cloudsValLabel.setForeground(Color.WHITE);
        detailGrid.add(createDetailCard("☁ Cloud Cover", cloudsValLabel, null));

        // Card 6: Sunrise / Sunset
        sunriseSunsetValLabel = new JLabel("06:00 / 18:00");
        sunriseSunsetValLabel.setFont(new Font("Segoe UI", Font.BOLD, 20));
        sunriseSunsetValLabel.setForeground(Color.WHITE);
        detailGrid.add(createDetailCard("🌅 Sunrise / Sunset", sunriseSunsetValLabel, null));

        gbc.gridx = 1;
        gbc.weightx = 0.55;
        gbc.insets = new Insets(0, 0, 0, 0);
        centerContainer.add(detailGrid, gbc);

        add(centerContainer, BorderLayout.CENTER);

        // 3. BOTTOM CONTROLS
        JPanel bottomPanel = new JPanel(new BorderLayout());
        bottomPanel.setOpaque(false);
        bottomPanel.setBorder(new EmptyBorder(10, 0, 0, 0));

        JPanel bottomLeft = new JPanel(new FlowLayout(FlowLayout.LEFT, 15, 0));
        bottomLeft.setOpaque(false);

        unitToggle = new JToggleButton("Unit: °C");
        unitToggle.setFont(new Font("Segoe UI", Font.BOLD, 12));
        unitToggle.setBackground(CARD_BG);
        unitToggle.setForeground(Color.WHITE);
        unitToggle.setFocusPainted(false);
        unitToggle.addActionListener(e -> {
            isCelsius = !unitToggle.isSelected();
            unitToggle.setText(isCelsius ? "Unit: °C" : "Unit: °F");
            updateDisplayValues();
        });
        bottomLeft.add(unitToggle);

        JPanel bottomRight = new JPanel(new FlowLayout(FlowLayout.RIGHT, 15, 0));
        bottomRight.setOpaque(false);

        autoRefreshCheck = new JCheckBox("Auto-Refresh");
        autoRefreshCheck.setFont(new Font("Segoe UI", Font.PLAIN, 12));
        autoRefreshCheck.setForeground(Color.WHITE);
        autoRefreshCheck.setOpaque(false);
        autoRefreshCheck.setSelected(true);

        JLabel intervalLabel = new JLabel("Interval (min):");
        intervalLabel.setFont(new Font("Segoe UI", Font.PLAIN, 12));
        intervalLabel.setForeground(TEXT_MUTED);

        intervalCombo = new JComboBox<>(new Integer[]{1, 2, 5, 10, 15, 30});
        intervalCombo.setSelectedItem(5);
        intervalCombo.setFont(new Font("Segoe UI", Font.PLAIN, 12));
        intervalCombo.setBackground(CARD_BG);
        intervalCombo.setForeground(Color.WHITE);

        bottomRight.add(autoRefreshCheck);
        bottomRight.add(intervalLabel);
        bottomRight.add(intervalCombo);

        bottomPanel.add(bottomLeft, BorderLayout.WEST);
        bottomPanel.add(bottomRight, BorderLayout.EAST);

        add(bottomPanel, BorderLayout.SOUTH);

        // Auto-refresh timer initialization
        autoRefreshTimer = new Timer(5 * 60 * 1000, e -> {
            if (autoRefreshCheck.isSelected()) {
                loadWeather(currentCity);
            }
        });
        autoRefreshTimer.start();

        ActionListener timerUpdateListener = e -> {
            Integer minutes = (Integer) intervalCombo.getSelectedItem();
            if (minutes != null && minutes > 0) {
                autoRefreshTimer.setDelay(minutes * 60 * 1000);
                autoRefreshTimer.restart();
            }
        };
        intervalCombo.addActionListener(timerUpdateListener);
        autoRefreshCheck.addActionListener(e -> {
            if (autoRefreshCheck.isSelected()) {
                autoRefreshTimer.restart();
            } else {
                autoRefreshTimer.stop();
            }
        });

        // Initial load
        loadWeather(currentCity);
    }

    private JPanel createCardPanel() {
        JPanel card = new JPanel();
        card.setBackground(CARD_BG);
        card.setBorder(BorderFactory.createCompoundBorder(
                new LineBorder(BORDER_COLOR, 1, true),
                new EmptyBorder(16, 16, 16, 16)
        ));
        return card;
    }

    private JPanel createDetailCard(String title, JLabel valueLabel, JComponent extraComponent) {
        JPanel card = createCardPanel();
        card.setLayout(new BorderLayout(5, 8));

        JLabel titleLbl = new JLabel(title);
        titleLbl.setFont(new Font("Segoe UI", Font.PLAIN, 13));
        titleLbl.setForeground(TEXT_MUTED);

        card.add(titleLbl, BorderLayout.NORTH);
        card.add(valueLabel, BorderLayout.CENTER);

        if (extraComponent != null) {
            card.add(extraComponent, BorderLayout.SOUTH);
        }
        return card;
    }

    /**
     * Asynchronously loads weather for the given city using SwingWorker.
     */
    public void loadWeather(String cityName) {
        if (cityName == null || cityName.isBlank()) {
            return;
        }
        this.currentCity = cityName.trim();
        progressBar.setVisible(true);
        refreshButton.setEnabled(false);

        SwingWorker<WeatherData, Void> worker = new SwingWorker<>() {
            @Override
            protected WeatherData doInBackground() {
                return apiClient.getCurrentWeather(currentCity);
            }

            @Override
            protected void done() {
                progressBar.setVisible(false);
                refreshButton.setEnabled(true);
                try {
                    WeatherData data = get();
                    if (data != null) {
                        currentWeatherData = data;
                        cachedWeatherData = data;
                        dataSourceBadge.setText(" API ");
                        dataSourceBadge.setBackground(PRIMARY_BLUE);
                        updateDisplayValues();
                    }
                } catch (InterruptedException ie) {
                    Thread.currentThread().interrupt();
                } catch (ExecutionException ee) {
                    handleLoadFailure(ee.getCause());
                }
            }
        };
        worker.execute();
    }

    private void handleLoadFailure(Throwable cause) {
        String msg = (cause != null && cause.getMessage() != null)
                ? cause.getMessage()
                : "Unable to connect to weather backend.";

        if (cachedWeatherData != null) {
            int opt = JOptionPane.showConfirmDialog(
                    this,
                    "Failed to fetch live weather:\n" + msg + "\n\nWould you like to display cached data?",
                    "Weather Data Error",
                    JOptionPane.YES_NO_OPTION,
                    JOptionPane.WARNING_MESSAGE
            );
            if (opt == JOptionPane.YES_OPTION) {
                currentWeatherData = cachedWeatherData;
                dataSourceBadge.setText(" CACHE ");
                dataSourceBadge.setBackground(new Color(180, 100, 0));
                updateDisplayValues();
            }
        } else {
            JOptionPane.showMessageDialog(
                    this,
                    "Failed to fetch weather for " + currentCity + ":\n" + msg,
                    "Weather Service Error",
                    JOptionPane.ERROR_MESSAGE
            );
        }
    }

    private void updateDisplayValues() {
        if (currentWeatherData == null) {
            return;
        }

        String city = currentWeatherData.getCityName();
        String country = currentWeatherData.getCountry();
        cityCountryLabel.setText(city + (country.isEmpty() ? "" : ", " + country));

        String recordedAt = currentWeatherData.getRecordedAt();
        if (recordedAt == null || recordedAt.isBlank()) {
            recordedAt = LocalDateTime.now().format(TIME_FORMATTER);
        }
        lastUpdatedLabel.setText("Last updated: " + recordedAt);

        // Temperatures
        double temp = currentWeatherData.getTemperature();
        double feels = currentWeatherData.getFeelsLike();
        double min = currentWeatherData.getTempMin();
        double max = currentWeatherData.getTempMax();

        tempLabel.setText(UnitConverter.formatTemperature(temp, isCelsius));
        feelsLikeLabel.setText("Feels like: " + UnitConverter.formatTemperature(feels, isCelsius));
        minMaxLabel.setText(String.format("Min: %s  •  Max: %s",
                UnitConverter.formatTemperature(min, isCelsius),
                UnitConverter.formatTemperature(max, isCelsius)));

        // Description & Icon
        conditionLabel.setText(currentWeatherData.getDescription());
        weatherIconLabel.setText(mapWeatherIcon(currentWeatherData.getIcon(), currentWeatherData.getWeatherMain()));

        // Detail cards
        int humidity = currentWeatherData.getHumidity();
        humidityValLabel.setText(humidity + "%");
        humidityBar.setValue(humidity);
        humidityBar.setString(humidity + "%");

        pressureValLabel.setText(currentWeatherData.getPressure() + " hPa");

        double windSpeed = currentWeatherData.getWindSpeed();
        int windDeg = currentWeatherData.getWindDeg();
        String windDir = UnitConverter.degreesToDirection(windDeg);
        windValLabel.setText(String.format("%.1f m/s (%s)", windSpeed, windDir));

        int visibilityMeters = currentWeatherData.getVisibility();
        if (visibilityMeters >= 1000) {
            visibilityValLabel.setText(String.format("%.1f km", visibilityMeters / 1000.0));
        } else {
            visibilityValLabel.setText(visibilityMeters + " m");
        }

        cloudsValLabel.setText(currentWeatherData.getClouds() + "%");

        sunriseSunsetValLabel.setText("06:00 / 18:00");
    }

    private String mapWeatherIcon(String iconCode, String weatherMain) {
        if (iconCode != null) {
            if (iconCode.startsWith("01")) return "☀️";
            if (iconCode.startsWith("02")) return "⛅";
            if (iconCode.startsWith("03") || iconCode.startsWith("04")) return "☁️";
            if (iconCode.startsWith("09") || iconCode.startsWith("10")) return "🌧️";
            if (iconCode.startsWith("11")) return "⛈️";
            if (iconCode.startsWith("13")) return "❄️";
            if (iconCode.startsWith("50")) return "🌫️";
        }
        if (weatherMain != null) {
            String m = weatherMain.toLowerCase();
            if (m.contains("rain")) return "🌧️";
            if (m.contains("cloud")) return "☁️";
            if (m.contains("snow")) return "❄️";
            if (m.contains("thunder")) return "⛈️";
            if (m.contains("clear")) return "☀️";
        }
        return "🌤️";
    }

    public void setCity(String cityName) {
        if (cityName != null && !cityName.isBlank()) {
            this.currentCity = cityName;
            loadWeather(cityName);
        }
    }

    public String getCurrentCity() {
        return currentCity;
    }
}
