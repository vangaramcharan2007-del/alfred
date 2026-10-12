package com.weatherintel.ui.panels;

import com.weatherintel.ui.services.ApiClient;
import com.weatherintel.ui.services.ApiClient.CityResult;
import com.weatherintel.ui.services.ApiClient.FavoriteData;
import com.weatherintel.ui.services.ApiClient.WeatherData;
import com.weatherintel.ui.services.UnitConverter;

import javax.swing.*;
import javax.swing.border.EmptyBorder;
import javax.swing.border.LineBorder;
import javax.swing.table.DefaultTableCellRenderer;
import javax.swing.table.DefaultTableModel;
import java.awt.*;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ExecutionException;

/**
 * Multi-city weather monitoring panel with live search, favorite persistence,
 * dynamic weather cards grid, and comparison side-by-side table.
 */
public class MultiCityPanel extends JPanel {

    private static final Color BG_DARK = new Color(0x1E, 0x1E, 0x1E);
    private static final Color CARD_BG = new Color(0x2D, 0x2D, 0x2D);
    private static final Color PRIMARY_BLUE = new Color(0x1E, 0x3E, 0x72);
    private static final Color SECONDARY_BLUE = new Color(0x21, 0x96, 0xF3);
    private static final Color ACCENT_ORANGE = new Color(0xFF, 0x98, 0x00);
    private static final Color TEXT_MUTED = new Color(170, 175, 185);
    private static final Color BORDER_COLOR = new Color(60, 65, 75);

    private static final long DEFAULT_USER_ID = 1L;

    private final ApiClient apiClient;

    // Search & Header
    private final JTextField searchField;
    private final JButton searchButton;
    private final JButton addCityButton;
    private final JComboBox<CityResult> searchResultsCombo;
    private final JProgressBar progressBar;

    // Center cards grid
    private final JPanel cardsGridPanel;
    private final JScrollPane cardsScrollPane;

    // Right comparison sidebar table
    private final DefaultTableModel comparisonTableModel;
    private final JTable comparisonTable;

    // Bottom action buttons
    private final JButton refreshAllButton;
    private final JButton addToFavoritesButton;
    private final JButton removeCityButton;

    // Monitoring list state: City Name -> WeatherData
    private final Map<String, WeatherData> monitoredCities = new LinkedHashMap<>();
    private String selectedCityForAction = null;

    public MultiCityPanel(ApiClient apiClient) {
        this.apiClient = apiClient != null ? apiClient : new ApiClient();

        setLayout(new BorderLayout(15, 15));
        setBackground(BG_DARK);
        setBorder(new EmptyBorder(15, 15, 15, 15));

        // 1. TOP SEARCH & FAVORITES BAR
        JPanel topBar = new JPanel(new BorderLayout(10, 8));
        topBar.setOpaque(false);

        JPanel searchControls = new JPanel(new FlowLayout(FlowLayout.LEFT, 10, 0));
        searchControls.setOpaque(false);

        JLabel searchLabel = new JLabel("Search City:");
        searchLabel.setFont(new Font("Segoe UI", Font.BOLD, 12));
        searchLabel.setForeground(Color.WHITE);

        searchField = new JTextField(14);
        searchField.setFont(new Font("Segoe UI", Font.PLAIN, 12));
        searchField.setBackground(CARD_BG);
        searchField.setForeground(Color.WHITE);
        searchField.setCaretColor(Color.WHITE);

        searchButton = new JButton("Search");
        searchButton.setFont(new Font("Segoe UI", Font.BOLD, 11));
        searchButton.setBackground(PRIMARY_BLUE);
        searchButton.setForeground(Color.WHITE);
        searchButton.setFocusPainted(false);
        searchButton.addActionListener(e -> executeCitySearch());

        searchResultsCombo = new JComboBox<>();
        searchResultsCombo.setFont(new Font("Segoe UI", Font.PLAIN, 12));
        searchResultsCombo.setBackground(CARD_BG);
        searchResultsCombo.setForeground(Color.WHITE);
        searchResultsCombo.setPreferredSize(new Dimension(180, 26));

        addCityButton = new JButton("+ Add to Monitor");
        addCityButton.setFont(new Font("Segoe UI", Font.BOLD, 11));
        addCityButton.setBackground(SECONDARY_BLUE);
        addCityButton.setForeground(Color.WHITE);
        addCityButton.setFocusPainted(false);
        addCityButton.addActionListener(e -> addSelectedSearchResult());

        searchControls.add(searchLabel);
        searchControls.add(searchField);
        searchControls.add(searchButton);
        searchControls.add(searchResultsCombo);
        searchControls.add(addCityButton);

        progressBar = new JProgressBar();
        progressBar.setIndeterminate(true);
        progressBar.setVisible(false);
        progressBar.setPreferredSize(new Dimension(100, 4));
        progressBar.setForeground(SECONDARY_BLUE);
        progressBar.setBackground(BG_DARK);

        topBar.add(searchControls, BorderLayout.CENTER);
        topBar.add(progressBar, BorderLayout.SOUTH);

        add(topBar, BorderLayout.NORTH);

        // 2. CENTER & RIGHT (SplitPane: Cards grid on Left, Comparison table on Right)
        cardsGridPanel = new JPanel(new GridLayout(0, 2, 12, 12));
        cardsGridPanel.setBackground(BG_DARK);

        cardsScrollPane = new JScrollPane(cardsGridPanel);
        cardsScrollPane.setBorder(BorderFactory.createTitledBorder(
                new LineBorder(BORDER_COLOR, 1, true),
                "Monitored Cities",
                0,
                0,
                new Font("Segoe UI", Font.BOLD, 12),
                Color.WHITE
        ));
        cardsScrollPane.getViewport().setBackground(BG_DARK);
        cardsScrollPane.getVerticalScrollBar().setUnitIncrement(16);

        // Right comparison table
        String[] cols = {"City", "Temp", "Condition", "Humidity", "Wind", "Pressure"};
        comparisonTableModel = new DefaultTableModel(cols, 0) {
            @Override
            public boolean isCellEditable(int row, int col) {
                return false;
            }
        };

        comparisonTable = new JTable(comparisonTableModel);
        comparisonTable.setFont(new Font("Segoe UI", Font.PLAIN, 12));
        comparisonTable.setRowHeight(26);
        comparisonTable.setBackground(CARD_BG);
        comparisonTable.setForeground(Color.WHITE);
        comparisonTable.setGridColor(BORDER_COLOR);
        comparisonTable.getTableHeader().setBackground(PRIMARY_BLUE);
        comparisonTable.getTableHeader().setForeground(Color.WHITE);
        comparisonTable.getTableHeader().setFont(new Font("Segoe UI", Font.BOLD, 12));

        // Color-coded cell renderer for temperature column (Column 1)
        comparisonTable.getColumnModel().getColumn(1).setCellRenderer(new TemperatureCellRenderer());

        DefaultTableCellRenderer centerRender = new DefaultTableCellRenderer();
        centerRender.setHorizontalAlignment(SwingConstants.CENTER);
        for (int i = 0; i < comparisonTable.getColumnCount(); i++) {
            if (i != 1) {
                comparisonTable.getColumnModel().getColumn(i).setCellRenderer(centerRender);
            }
        }

        comparisonTable.getSelectionModel().addListSelectionListener(e -> {
            if (!e.getValueIsAdjusting()) {
                int row = comparisonTable.getSelectedRow();
                if (row >= 0) {
                    selectedCityForAction = (String) comparisonTable.getValueAt(row, 0);
                }
            }
        });

        JScrollPane compScroll = new JScrollPane(comparisonTable);
        compScroll.setBorder(BorderFactory.createTitledBorder(
                new LineBorder(BORDER_COLOR, 1, true),
                "City Comparison",
                0,
                0,
                new Font("Segoe UI", Font.BOLD, 12),
                Color.WHITE
        ));
        compScroll.getViewport().setBackground(CARD_BG);
        compScroll.setPreferredSize(new Dimension(380, 200));

        JSplitPane centerSplit = new JSplitPane(JSplitPane.HORIZONTAL_SPLIT, cardsScrollPane, compScroll);
        centerSplit.setDividerLocation(520);
        centerSplit.setOpaque(false);
        centerSplit.setBorder(null);

        add(centerSplit, BorderLayout.CENTER);

        // 3. BOTTOM ACTIONS
        JPanel bottomBar = new JPanel(new FlowLayout(FlowLayout.RIGHT, 15, 0));
        bottomBar.setOpaque(false);

        addToFavoritesButton = new JButton("★ Add to Favorites");
        addToFavoritesButton.setFont(new Font("Segoe UI", Font.BOLD, 12));
        addToFavoritesButton.setBackground(ACCENT_ORANGE);
        addToFavoritesButton.setForeground(Color.WHITE);
        addToFavoritesButton.setFocusPainted(false);
        addToFavoritesButton.addActionListener(e -> persistFavoriteCity());

        removeCityButton = new JButton("✖ Remove City");
        removeCityButton.setFont(new Font("Segoe UI", Font.BOLD, 12));
        removeCityButton.setBackground(new Color(180, 40, 40));
        removeCityButton.setForeground(Color.WHITE);
        removeCityButton.setFocusPainted(false);
        removeCityButton.addActionListener(e -> removeSelectedCity());

        refreshAllButton = new JButton("↻ Refresh All");
        refreshAllButton.setFont(new Font("Segoe UI", Font.BOLD, 12));
        refreshAllButton.setBackground(SECONDARY_BLUE);
        refreshAllButton.setForeground(Color.WHITE);
        refreshAllButton.setFocusPainted(false);
        refreshAllButton.addActionListener(e -> refreshAllCities());

        bottomBar.add(addToFavoritesButton);
        bottomBar.add(removeCityButton);
        bottomBar.add(refreshAllButton);

        add(bottomBar, BorderLayout.SOUTH);

        // Seed with default initial cities
        addCityToMonitor("London");
        addCityToMonitor("Tokyo");
        addCityToMonitor("New York");
        loadUserFavorites();
    }

    private void executeCitySearch() {
        String query = searchField.getText().trim();
        if (query.isEmpty()) return;

        progressBar.setVisible(true);
        searchButton.setEnabled(false);

        SwingWorker<List<CityResult>, Void> worker = new SwingWorker<>() {
            @Override
            protected List<CityResult> doInBackground() {
                return apiClient.searchCities(query);
            }

            @Override
            protected void done() {
                progressBar.setVisible(false);
                searchButton.setEnabled(true);
                try {
                    List<CityResult> results = get();
                    searchResultsCombo.removeAllItems();
                    if (results != null && !results.isEmpty()) {
                        for (CityResult c : results) {
                            searchResultsCombo.addItem(c);
                        }
                    } else {
                        // Fallback: create mock result if backend returns empty
                        searchResultsCombo.addItem(new CityResult(100L, query, "US", "", 0, 0));
                    }
                } catch (Exception ex) {
                    searchResultsCombo.removeAllItems();
                    searchResultsCombo.addItem(new CityResult(100L, query, "US", "", 0, 0));
                }
            }
        };
        worker.execute();
    }

    private void addSelectedSearchResult() {
        CityResult res = (CityResult) searchResultsCombo.getSelectedItem();
        if (res != null) {
            addCityToMonitor(res.getName());
        } else if (!searchField.getText().isBlank()) {
            addCityToMonitor(searchField.getText().trim());
        }
    }

    public void addCityToMonitor(String cityName) {
        if (cityName == null || cityName.isBlank() || monitoredCities.containsKey(cityName)) {
            return;
        }

        progressBar.setVisible(true);

        SwingWorker<WeatherData, Void> worker = new SwingWorker<>() {
            @Override
            protected WeatherData doInBackground() {
                return apiClient.getCurrentWeather(cityName);
            }

            @Override
            protected void done() {
                progressBar.setVisible(false);
                try {
                    WeatherData data = get();
                    if (data != null) {
                        monitoredCities.put(data.getCityName(), data);
                        refreshUI();
                    }
                } catch (Exception ex) {
                    JOptionPane.showMessageDialog(
                            MultiCityPanel.this,
                            "Could not load weather for " + cityName + ": " + ex.getMessage(),
                            "Add City Error",
                            JOptionPane.WARNING_MESSAGE
                    );
                }
            }
        };
        worker.execute();
    }

    public void refreshAllCities() {
        if (monitoredCities.isEmpty()) return;
        progressBar.setVisible(true);
        refreshAllButton.setEnabled(false);

        List<String> cities = new ArrayList<>(monitoredCities.keySet());

        SwingWorker<List<WeatherData>, Void> worker = new SwingWorker<>() {
            @Override
            protected List<WeatherData> doInBackground() {
                List<WeatherData> results = new ArrayList<>();
                for (String c : cities) {
                    try {
                        results.add(apiClient.getCurrentWeather(c));
                    } catch (Exception ignored) {
                    }
                }
                return results;
            }

            @Override
            protected void done() {
                progressBar.setVisible(false);
                refreshAllButton.setEnabled(true);
                try {
                    List<WeatherData> list = get();
                    for (WeatherData wd : list) {
                        monitoredCities.put(wd.getCityName(), wd);
                    }
                    refreshUI();
                } catch (Exception ignored) {
                }
            }
        };
        worker.execute();
    }

    private void removeSelectedCity() {
        if (selectedCityForAction != null && monitoredCities.containsKey(selectedCityForAction)) {
            monitoredCities.remove(selectedCityForAction);
            selectedCityForAction = null;
            refreshUI();
        } else {
            JOptionPane.showMessageDialog(this, "Please select a city to remove from the comparison table.");
        }
    }

    private void persistFavoriteCity() {
        if (selectedCityForAction == null) {
            JOptionPane.showMessageDialog(this, "Please select a city from the comparison table to add to favorites.");
            return;
        }

        WeatherData data = monitoredCities.get(selectedCityForAction);
        if (data == null) return;

        progressBar.setVisible(true);
        SwingWorker<Void, Void> worker = new SwingWorker<>() {
            @Override
            protected Void doInBackground() {
                long cityId = data.getId() != null ? data.getId() : 1L;
                apiClient.addFavorite(DEFAULT_USER_ID, cityId);
                return null;
            }

            @Override
            protected void done() {
                progressBar.setVisible(false);
                JOptionPane.showMessageDialog(MultiCityPanel.this, selectedCityForAction + " added to favorites!");
            }
        };
        worker.execute();
    }

    private void loadUserFavorites() {
        SwingWorker<List<FavoriteData>, Void> worker = new SwingWorker<>() {
            @Override
            protected List<FavoriteData> doInBackground() {
                return apiClient.getFavorites(DEFAULT_USER_ID);
            }

            @Override
            protected void done() {
                try {
                    List<FavoriteData> favs = get();
                    if (favs != null) {
                        for (FavoriteData f : favs) {
                            if (!monitoredCities.containsKey(f.getCityName())) {
                                addCityToMonitor(f.getCityName());
                            }
                        }
                    }
                } catch (Exception ignored) {
                }
            }
        };
        worker.execute();
    }

    private void refreshUI() {
        // Rebuild cards
        cardsGridPanel.removeAll();
        comparisonTableModel.setRowCount(0);

        for (Map.Entry<String, WeatherData> entry : monitoredCities.entrySet()) {
            WeatherData wd = entry.getValue();
            cardsGridPanel.add(createCityCard(wd));

            comparisonTableModel.addRow(new Object[]{
                    wd.getCityName(),
                    String.format("%.1f°C", wd.getTemperature()),
                    wd.getWeatherMain(),
                    wd.getHumidity() + "%",
                    String.format("%.1f m/s", wd.windSpeed()),
                    wd.getPressure() + " hPa"
            });
        }

        cardsGridPanel.revalidate();
        cardsGridPanel.repaint();
    }

    private JPanel createCityCard(WeatherData wd) {
        JPanel card = new JPanel(new BorderLayout(8, 8));
        card.setBackground(CARD_BG);
        card.setBorder(BorderFactory.createCompoundBorder(
                new LineBorder(BORDER_COLOR, 1, true),
                new EmptyBorder(12, 14, 12, 14)
        ));

        // Top: City name & Temp
        JPanel top = new JPanel(new BorderLayout());
        top.setOpaque(false);

        JLabel nameLbl = new JLabel(wd.getCityName() + ", " + wd.getCountry());
        nameLbl.setFont(new Font("Segoe UI", Font.BOLD, 15));
        nameLbl.setForeground(Color.WHITE);

        JLabel tempLbl = new JLabel(String.format("%.1f°C", wd.getTemperature()));
        tempLbl.setFont(new Font("Segoe UI", Font.BOLD, 20));
        tempLbl.setForeground(SECONDARY_BLUE);

        top.add(nameLbl, BorderLayout.WEST);
        top.add(tempLbl, BorderLayout.EAST);

        // Center: Condition & Icon
        JPanel mid = new JPanel(new FlowLayout(FlowLayout.LEFT, 8, 4));
        mid.setOpaque(false);

        JLabel iconLbl = new JLabel(mapIconEmoji(wd.getWeatherMain()));
        iconLbl.setFont(new Font("Segoe UI Emoji", Font.PLAIN, 22));

        JLabel condLbl = new JLabel(wd.getDescription());
        condLbl.setFont(new Font("Segoe UI", Font.PLAIN, 12));
        condLbl.setForeground(new Color(220, 225, 235));

        mid.add(iconLbl);
        mid.add(condLbl);

        // Bottom: Humidity & Wind
        JPanel btm = new JPanel(new BorderLayout());
        btm.setOpaque(false);

        JLabel statsLbl = new JLabel(String.format("💧 Humidity: %d%%    💨 Wind: %.1f m/s",
                wd.getHumidity(), wd.getWindSpeed()));
        statsLbl.setFont(new Font("Segoe UI", Font.PLAIN, 11));
        statsLbl.setForeground(TEXT_MUTED);

        btm.add(statsLbl, BorderLayout.WEST);

        card.add(top, BorderLayout.NORTH);
        card.add(mid, BorderLayout.CENTER);
        card.add(btm, BorderLayout.SOUTH);

        return card;
    }

    private String mapIconEmoji(String weatherMain) {
        if (weatherMain == null) return "🌤️";
        String m = weatherMain.toLowerCase();
        if (m.contains("rain")) return "🌧️";
        if (m.contains("cloud")) return "☁️";
        if (m.contains("snow")) return "❄️";
        if (m.contains("thunder")) return "⛈️";
        if (m.contains("clear")) return "☀️";
        return "🌤️";
    }

    /**
     * Custom cell renderer for the temperature column:
     * Blue for cold (<10°C), Green for mild (10-25°C), Red for hot (>25°C)
     */
    private static class TemperatureCellRenderer extends DefaultTableCellRenderer {
        public TemperatureCellRenderer() {
            setHorizontalAlignment(SwingConstants.CENTER);
        }

        @Override
        public Component getTableCellRendererComponent(JTable table, Object value,
                                                       boolean isSelected, boolean hasFocus,
                                                       int row, int column) {
            Component c = super.getTableCellRendererComponent(table, value, isSelected, hasFocus, row, column);
            if (value != null) {
                String valStr = value.toString().replace("°C", "").trim();
                try {
                    double temp = Double.parseDouble(valStr);
                    if (temp < 10.0) {
                        c.setForeground(new Color(100, 180, 255)); // cold blue
                    } else if (temp <= 25.0) {
                        c.setForeground(new Color(120, 220, 130)); // mild green
                    } else {
                        c.setForeground(new Color(255, 110, 100)); // hot red
                    }
                } catch (NumberFormatException ignored) {
                    c.setForeground(Color.WHITE);
                }
            }
            return c;
        }
    }
}
