package com.weatherintel.ui.panels;

import com.weatherintel.ui.services.ApiClient;
import com.weatherintel.ui.services.ApiClient.ForecastData;
import com.weatherintel.ui.services.ApiClient.ForecastItem;
import com.weatherintel.ui.services.UnitConverter;
import org.jfree.chart.ChartFactory;
import org.jfree.chart.ChartPanel;
import org.jfree.chart.JFreeChart;
import org.jfree.chart.axis.DateAxis;
import org.jfree.chart.axis.NumberAxis;
import org.jfree.chart.plot.XYPlot;
import org.jfree.chart.renderer.xy.XYLineAndShapeRenderer;
import org.jfree.data.time.Hour;
import org.jfree.data.time.Minute;
import org.jfree.data.time.TimeSeries;
import org.jfree.data.time.TimeSeriesCollection;

import javax.swing.*;
import javax.swing.border.EmptyBorder;
import javax.swing.border.LineBorder;
import javax.swing.table.DefaultTableCellRenderer;
import javax.swing.table.DefaultTableModel;
import javax.swing.table.TableRowSorter;
import java.awt.*;
import java.text.SimpleDateFormat;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.concurrent.ExecutionException;

/**
 * Forecast panel displaying 5-day / 3-hour forecasts with custom cards,
 * JFreeChart temperature trend lines, and a sortable/filterable JTable.
 */
public class ForecastPanel extends JPanel {

    private static final Color BG_DARK = new Color(0x1E, 0x1E, 0x1E);
    private static final Color CARD_BG = new Color(0x2D, 0x2D, 0x2D);
    private static final Color PRIMARY_BLUE = new Color(0x1E, 0x3E, 0x72);
    private static final Color SECONDARY_BLUE = new Color(0x21, 0x96, 0xF3);
    private static final Color ACCENT_ORANGE = new Color(0xFF, 0x98, 0x00);
    private static final Color TEXT_MUTED = new Color(170, 175, 185);
    private static final Color BORDER_COLOR = new Color(60, 65, 75);

    private static final DateTimeFormatter PARSER_FMT = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

    private final ApiClient apiClient;

    // Top Controls
    private final JComboBox<String> citySelectorCombo;
    private final JLabel dateRangeLabel;
    private final JProgressBar progressBar;
    private final JButton fetchButton;

    // Center Split: Left cards, Right chart
    private final JPanel cardsContainer;
    private final JScrollPane cardsScrollPane;
    private ChartPanel chartPanel;
    private JFreeChart temperatureChart;
    private final TimeSeriesCollection chartDataset;

    // Bottom Table
    private final DefaultTableModel tableModel;
    private final JTable forecastTable;
    private final TableRowSorter<DefaultTableModel> tableSorter;
    private final JComboBox<String> conditionFilterCombo;

    private String currentCity = "London";
    private List<ForecastItem> currentItems = new ArrayList<>();

    public ForecastPanel(ApiClient apiClient) {
        this.apiClient = apiClient != null ? apiClient : new ApiClient();

        setLayout(new BorderLayout(15, 15));
        setBackground(BG_DARK);
        setBorder(new EmptyBorder(15, 15, 15, 15));

        // 1. TOP BAR
        JPanel topBar = new JPanel(new BorderLayout(10, 10));
        topBar.setOpaque(false);

        JPanel topLeft = new JPanel(new FlowLayout(FlowLayout.LEFT, 12, 0));
        topLeft.setOpaque(false);

        JLabel cityLabel = new JLabel("City:");
        cityLabel.setFont(new Font("Segoe UI", Font.BOLD, 13));
        cityLabel.setForeground(Color.WHITE);

        citySelectorCombo = new JComboBox<>(new String[]{"London", "New York", "Tokyo", "Paris", "Berlin", "San Francisco"});
        citySelectorCombo.setEditable(true);
        citySelectorCombo.setFont(new Font("Segoe UI", Font.PLAIN, 13));
        citySelectorCombo.setBackground(CARD_BG);
        citySelectorCombo.setForeground(Color.WHITE);
        citySelectorCombo.setPreferredSize(new Dimension(160, 28));

        fetchButton = new JButton("Get Forecast");
        fetchButton.setFont(new Font("Segoe UI", Font.BOLD, 12));
        fetchButton.setBackground(SECONDARY_BLUE);
        fetchButton.setForeground(Color.WHITE);
        fetchButton.setFocusPainted(false);
        fetchButton.setCursor(new Cursor(Cursor.HAND_CURSOR));
        fetchButton.addActionListener(e -> {
            Object sel = citySelectorCombo.getSelectedItem();
            if (sel != null && !sel.toString().isBlank()) {
                loadForecast(sel.toString().trim());
            }
        });

        dateRangeLabel = new JLabel("5-Day / 3-Hour Forecast | OpenWeather Free Tier");
        dateRangeLabel.setFont(new Font("Segoe UI", Font.ITALIC, 12));
        dateRangeLabel.setForeground(TEXT_MUTED);

        topLeft.add(cityLabel);
        topLeft.add(citySelectorCombo);
        topLeft.add(fetchButton);
        topLeft.add(Box.createHorizontalStrut(15));
        topLeft.add(dateRangeLabel);

        progressBar = new JProgressBar();
        progressBar.setIndeterminate(true);
        progressBar.setVisible(false);
        progressBar.setPreferredSize(new Dimension(100, 4));
        progressBar.setForeground(SECONDARY_BLUE);
        progressBar.setBackground(BG_DARK);

        topBar.add(topLeft, BorderLayout.CENTER);
        topBar.add(progressBar, BorderLayout.SOUTH);

        add(topBar, BorderLayout.NORTH);

        // 2. CENTER SPLIT PANE (Cards on Left, JFreeChart on Right)
        cardsContainer = new JPanel();
        cardsContainer.setLayout(new BoxLayout(cardsContainer, BoxLayout.Y_AXIS));
        cardsContainer.setBackground(BG_DARK);

        cardsScrollPane = new JScrollPane(cardsContainer);
        cardsScrollPane.setBorder(BorderFactory.createTitledBorder(
                new LineBorder(BORDER_COLOR, 1, true),
                "Forecast Timeline",
                0,
                0,
                new Font("Segoe UI", Font.BOLD, 12),
                Color.WHITE
        ));
        cardsScrollPane.getViewport().setBackground(BG_DARK);
        cardsScrollPane.getVerticalScrollBar().setUnitIncrement(16);
        cardsScrollPane.setPreferredSize(new Dimension(320, 240));

        // JFreeChart Setup
        chartDataset = new TimeSeriesCollection();
        temperatureChart = createTemperatureChart(chartDataset);
        chartPanel = new ChartPanel(temperatureChart);
        chartPanel.setBackground(BG_DARK);
        chartPanel.setBorder(BorderFactory.createTitledBorder(
                new LineBorder(BORDER_COLOR, 1, true),
                "Temperature Trend (°C)",
                0,
                0,
                new Font("Segoe UI", Font.BOLD, 12),
                Color.WHITE
        ));
        chartPanel.setPopupMenu(null);

        JSplitPane centerSplit = new JSplitPane(JSplitPane.HORIZONTAL_SPLIT, cardsScrollPane, chartPanel);
        centerSplit.setDividerLocation(360);
        centerSplit.setOpaque(false);
        centerSplit.setBorder(null);

        // 3. BOTTOM TABLE PANEL
        JPanel bottomTablePanel = new JPanel(new BorderLayout(5, 8));
        bottomTablePanel.setOpaque(false);
        bottomTablePanel.setPreferredSize(new Dimension(800, 220));

        JPanel tableToolbar = new JPanel(new FlowLayout(FlowLayout.LEFT, 10, 0));
        tableToolbar.setOpaque(false);

        JLabel filterLbl = new JLabel("Filter Condition:");
        filterLbl.setFont(new Font("Segoe UI", Font.PLAIN, 12));
        filterLbl.setForeground(Color.WHITE);

        conditionFilterCombo = new JComboBox<>(new String[]{"All Conditions", "Clear", "Clouds", "Rain", "Snow", "Drizzle"});
        conditionFilterCombo.setFont(new Font("Segoe UI", Font.PLAIN, 12));
        conditionFilterCombo.setBackground(CARD_BG);
        conditionFilterCombo.setForeground(Color.WHITE);
        conditionFilterCombo.addActionListener(e -> applyConditionFilter());

        JLabel attributionLbl = new JLabel("Attribution: OpenWeather Free Tier (3-Hour Steps)");
        attributionLbl.setFont(new Font("Segoe UI", Font.ITALIC, 11));
        attributionLbl.setForeground(TEXT_MUTED);

        tableToolbar.add(filterLbl);
        tableToolbar.add(conditionFilterCombo);
        tableToolbar.add(Box.createHorizontalStrut(20));
        tableToolbar.add(attributionLbl);

        // Table Columns: Date/Time, Temp, Feels Like, Min, Max, Humidity, Wind, Precip%, Condition
        String[] columns = {"Date / Time", "Temp (°C)", "Feels Like", "Min", "Max", "Humidity", "Wind", "Precip %", "Condition"};
        tableModel = new DefaultTableModel(columns, 0) {
            @Override
            public boolean isCellEditable(int row, int col) {
                return false;
            }
        };

        forecastTable = new JTable(tableModel);
        forecastTable.setFont(new Font("Segoe UI", Font.PLAIN, 12));
        forecastTable.setRowHeight(24);
        forecastTable.setBackground(CARD_BG);
        forecastTable.setForeground(Color.WHITE);
        forecastTable.setGridColor(BORDER_COLOR);
        forecastTable.getTableHeader().setBackground(PRIMARY_BLUE);
        forecastTable.getTableHeader().setForeground(Color.WHITE);
        forecastTable.getTableHeader().setFont(new Font("Segoe UI", Font.BOLD, 12));

        tableSorter = new TableRowSorter<>(tableModel);
        forecastTable.setRowSorter(tableSorter);

        // Center align cell renderer
        DefaultTableCellRenderer centerRenderer = new DefaultTableCellRenderer();
        centerRenderer.setHorizontalAlignment(SwingConstants.CENTER);
        for (int i = 0; i < forecastTable.getColumnCount(); i++) {
            forecastTable.getColumnModel().getColumn(i).setCellRenderer(centerRenderer);
        }

        JScrollPane tableScroll = new JScrollPane(forecastTable);
        tableScroll.setBorder(new LineBorder(BORDER_COLOR, 1, true));
        tableScroll.getViewport().setBackground(CARD_BG);

        bottomTablePanel.add(tableToolbar, BorderLayout.NORTH);
        bottomTablePanel.add(tableScroll, BorderLayout.CENTER);

        // Combine Center and Bottom in a vertical split or BorderLayout
        JSplitPane mainSplit = new JSplitPane(JSplitPane.VERTICAL_SPLIT, centerSplit, bottomTablePanel);
        mainSplit.setDividerLocation(340);
        mainSplit.setOpaque(false);
        mainSplit.setBorder(null);

        add(mainSplit, BorderLayout.CENTER);

        // Initial Load
        loadForecast(currentCity);
    }

    private JFreeChart createTemperatureChart(TimeSeriesCollection dataset) {
        JFreeChart chart = ChartFactory.createTimeSeriesChart(
                null,
                "Time",
                "Temperature (°C)",
                dataset,
                false,
                true,
                false
        );

        chart.setBackgroundPaint(BG_DARK);

        XYPlot plot = chart.getXYPlot();
        plot.setBackgroundPaint(new Color(25, 27, 33));
        plot.setDomainGridlinePaint(new Color(50, 56, 68));
        plot.setRangeGridlinePaint(new Color(50, 56, 68));
        plot.setOutlinePaint(BORDER_COLOR);

        XYLineAndShapeRenderer renderer = new XYLineAndShapeRenderer(true, true);
        renderer.setSeriesPaint(0, SECONDARY_BLUE);
        renderer.setSeriesStroke(0, new BasicStroke(2.5f));
        plot.setRenderer(renderer);

        DateAxis domainAxis = (DateAxis) plot.getDomainAxis();
        domainAxis.setDateFormatOverride(new SimpleDateFormat("MM-dd HH:mm"));
        domainAxis.setTickLabelPaint(TEXT_MUTED);
        domainAxis.setLabelPaint(Color.WHITE);

        NumberAxis rangeAxis = (NumberAxis) plot.getRangeAxis();
        rangeAxis.setTickLabelPaint(TEXT_MUTED);
        rangeAxis.setLabelPaint(Color.WHITE);
        rangeAxis.setAutoRangeIncludesZero(false);

        return chart;
    }

    public void loadForecast(String cityName) {
        if (cityName == null || cityName.isBlank()) return;
        this.currentCity = cityName.trim();

        progressBar.setVisible(true);
        fetchButton.setEnabled(false);

        SwingWorker<ForecastData, Void> worker = new SwingWorker<>() {
            @Override
            protected ForecastData doInBackground() {
                return apiClient.getForecast(currentCity);
            }

            @Override
            protected void done() {
                progressBar.setVisible(false);
                fetchButton.setEnabled(true);
                try {
                    ForecastData data = get();
                    if (data != null) {
                        currentItems = data.getItems();
                        populateForecastUI(data);
                    }
                } catch (InterruptedException ie) {
                    Thread.currentThread().interrupt();
                } catch (ExecutionException ee) {
                    JOptionPane.showMessageDialog(
                            ForecastPanel.this,
                            "Failed to load forecast for " + currentCity + ":\n" +
                                    (ee.getCause() != null ? ee.getCause().getMessage() : ee.getMessage()),
                            "Forecast Error",
                            JOptionPane.ERROR_MESSAGE
                    );
                }
            }
        };
        worker.execute();
    }

    private void populateForecastUI(ForecastData data) {
        // 1. Rebuild Cards
        cardsContainer.removeAll();
        TimeSeries series = new TimeSeries("Temperature");

        tableModel.setRowCount(0);

        List<ForecastItem> items = data.getItems();
        for (ForecastItem item : items) {
            cardsContainer.add(createForecastCard(item));
            cardsContainer.add(Box.createVerticalStrut(8));

            // Chart data point
            try {
                String dtTxt = item.getDtTxt();
                if (dtTxt != null && !dtTxt.isBlank()) {
                    LocalDateTime dt = LocalDateTime.parse(dtTxt, PARSER_FMT);
                    Date date = java.sql.Timestamp.valueOf(dt);
                    series.addOrUpdate(new Minute(date), item.getTemperature());
                }
            } catch (Exception ignored) {
            }

            // Table row
            tableModel.addRow(new Object[]{
                    item.getDtTxt(),
                    String.format("%.1f", item.getTemperature()),
                    String.format("%.1f", item.getFeelsLike()),
                    String.format("%.1f", item.getTempMin()),
                    String.format("%.1f", item.getTempMax()),
                    item.getHumidity() + "%",
                    String.format("%.1f m/s", item.getWindSpeed()),
                    String.format("%.0f%%", item.getPop() * 100),
                    item.getWeatherMain() + " (" + item.getDescription() + ")"
            });
        }

        cardsContainer.revalidate();
        cardsContainer.repaint();

        // 2. Update chart
        chartDataset.removeAllSeries();
        chartDataset.addSeries(series);

        // 3. Update info label
        dateRangeLabel.setText(String.format("Forecast for %s, %s | %d intervals",
                data.getCityName(), data.getCountry(), items.size()));
    }

    private JPanel createForecastCard(ForecastItem item) {
        JPanel card = new JPanel(new BorderLayout(8, 4));
        card.setMaximumSize(new Dimension(Integer.MAX_VALUE, 75));
        card.setPreferredSize(new Dimension(300, 75));

        // Dynamic background based on temperature
        double temp = item.getTemperature();
        Color cardColor;
        if (temp < 5.0) {
            cardColor = new Color(25, 45, 75); // Cold blue
        } else if (temp < 22.0) {
            cardColor = new Color(35, 55, 45); // Mild green
        } else {
            cardColor = new Color(75, 45, 30); // Warm red/orange
        }
        card.setBackground(cardColor);
        card.setBorder(BorderFactory.createCompoundBorder(
                new LineBorder(BORDER_COLOR, 1, true),
                new EmptyBorder(6, 10, 6, 10)
        ));

        // Left: Time & Condition
        JPanel left = new JPanel();
        left.setLayout(new BoxLayout(left, BoxLayout.Y_AXIS));
        left.setOpaque(false);

        JLabel timeLbl = new JLabel(item.getDtTxt());
        timeLbl.setFont(new Font("Segoe UI", Font.BOLD, 12));
        timeLbl.setForeground(Color.WHITE);

        JLabel condLbl = new JLabel(item.getWeatherMain() + " • " + item.getDescription());
        condLbl.setFont(new Font("Segoe UI", Font.PLAIN, 11));
        condLbl.setForeground(TEXT_MUTED);

        JLabel detailLbl = new JLabel(String.format("💧 %d%%  •  💨 %.1f m/s  •  🌧 %.0f%%",
                item.getHumidity(), item.getWindSpeed(), item.getPop() * 100));
        detailLbl.setFont(new Font("Segoe UI", Font.PLAIN, 10));
        detailLbl.setForeground(new Color(200, 210, 225));

        left.add(timeLbl);
        left.add(condLbl);
        left.add(detailLbl);

        // Right: Big temp & icon
        JPanel right = new JPanel(new FlowLayout(FlowLayout.RIGHT, 6, 8));
        right.setOpaque(false);

        JLabel iconLbl = new JLabel(getWeatherEmoji(item.getWeatherMain()));
        iconLbl.setFont(new Font("Segoe UI Emoji", Font.PLAIN, 24));

        JLabel tempLbl = new JLabel(String.format("%.1f°C", item.getTemperature()));
        tempLbl.setFont(new Font("Segoe UI", Font.BOLD, 18));
        tempLbl.setForeground(Color.WHITE);

        right.add(iconLbl);
        right.add(tempLbl);

        card.add(left, BorderLayout.CENTER);
        card.add(right, BorderLayout.EAST);

        return card;
    }

    private void applyConditionFilter() {
        String selected = (String) conditionFilterCombo.getSelectedItem();
        if (selected == null || selected.equals("All Conditions")) {
            tableSorter.setRowFilter(null);
        } else {
            tableSorter.setRowFilter(RowFilter.regexFilter("(?i)" + selected, 8));
        }
    }

    private String getWeatherEmoji(String weatherMain) {
        if (weatherMain == null) return "🌤️";
        String m = weatherMain.toLowerCase();
        if (m.contains("rain")) return "🌧️";
        if (m.contains("cloud")) return "☁️";
        if (m.contains("snow")) return "❄️";
        if (m.contains("thunder")) return "⛈️";
        if (m.contains("clear")) return "☀️";
        if (m.contains("drizzle")) return "🌦️";
        return "🌤️";
    }
}
