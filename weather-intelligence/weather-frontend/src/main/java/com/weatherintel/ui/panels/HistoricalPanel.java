package com.weatherintel.ui.panels;

import com.weatherintel.ui.services.ApiClient;
import com.weatherintel.ui.services.ApiClient.AnalyticsSummaryData;
import com.weatherintel.ui.services.ApiClient.HistoryPage;
import com.weatherintel.ui.services.ApiClient.WeatherData;
import org.jfree.chart.ChartFactory;
import org.jfree.chart.ChartPanel;
import org.jfree.chart.JFreeChart;
import org.jfree.chart.axis.DateAxis;
import org.jfree.chart.axis.NumberAxis;
import org.jfree.chart.plot.XYPlot;
import org.jfree.chart.renderer.xy.XYLineAndShapeRenderer;
import org.jfree.data.time.Minute;
import org.jfree.data.time.TimeSeries;
import org.jfree.data.time.TimeSeriesCollection;

import javax.swing.*;
import javax.swing.border.EmptyBorder;
import javax.swing.border.LineBorder;
import javax.swing.table.DefaultTableCellRenderer;
import javax.swing.table.DefaultTableModel;
import java.awt.*;
import java.io.File;
import java.io.FileOutputStream;
import java.text.SimpleDateFormat;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;
import java.util.Calendar;
import java.util.Date;
import java.util.List;
import java.util.concurrent.ExecutionException;

/**
 * Historical weather data and analytics panel.
 * Includes date range pickers, JFreeChart multi-series trends (temperature, humidity, pressure),
 * paginated historical readings table, computed statistics card, period comparison, and CSV export.
 */
public class HistoricalPanel extends JPanel {

    private static final Color BG_DARK = new Color(0x1E, 0x1E, 0x1E);
    private static final Color CARD_BG = new Color(0x2D, 0x2D, 0x2D);
    private static final Color PRIMARY_BLUE = new Color(0x1E, 0x3E, 0x72);
    private static final Color SECONDARY_BLUE = new Color(0x21, 0x96, 0xF3);
    private static final Color ACCENT_ORANGE = new Color(0xFF, 0x98, 0x00);
    private static final Color TEXT_MUTED = new Color(170, 175, 185);
    private static final Color BORDER_COLOR = new Color(60, 65, 75);

    private static final DateTimeFormatter ISO_DATE_FMT = DateTimeFormatter.ofPattern("yyyy-MM-dd");
    private static final DateTimeFormatter RECORDED_FMT = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

    private final ApiClient apiClient;

    // Top Controls
    private final JComboBox<String> cityCombo;
    private final JSpinner startDateSpinner;
    private final JSpinner endDateSpinner;
    private final JButton filterButton;
    private final JProgressBar progressBar;

    // Center Split: Chart (top), Table (bottom)
    private final TimeSeriesCollection chartDataset;
    private final ChartPanel chartPanel;
    private final DefaultTableModel historyTableModel;
    private final JTable historyTable;
    private final JLabel pageInfoLabel;
    private final JButton prevPageButton;
    private final JButton nextPageButton;

    // Right Analytics Summary Card
    private final JLabel avgTempLabel;
    private final JLabel minTempLabel;
    private final JLabel maxTempLabel;
    private final JLabel avgHumidityLabel;
    private final JLabel avgPressureLabel;
    private final JLabel avgWindLabel;
    private final JLabel totalRainLabel;

    // Bottom Controls & Period Comparison
    private final JButton exportCsvButton;
    private final JButton comparePeriodButton;
    private final JLabel comparisonResultLabel;

    // Pagination & Filter State
    private long currentCityId = 1L;
    private int currentPage = 0;
    private static final int PAGE_SIZE = 15;
    private int totalPages = 1;

    public HistoricalPanel(ApiClient apiClient) {
        this.apiClient = apiClient != null ? apiClient : new ApiClient();

        setLayout(new BorderLayout(15, 15));
        setBackground(BG_DARK);
        setBorder(new EmptyBorder(15, 15, 15, 15));

        // 1. TOP CONTROLS BAR
        JPanel topBar = new JPanel(new BorderLayout(10, 8));
        topBar.setOpaque(false);

        JPanel filterRow = new JPanel(new FlowLayout(FlowLayout.LEFT, 12, 0));
        filterRow.setOpaque(false);

        JLabel cityLbl = new JLabel("City:");
        cityLbl.setFont(new Font("Segoe UI", Font.BOLD, 12));
        cityLbl.setForeground(Color.WHITE);

        cityCombo = new JComboBox<>(new String[]{"London", "New York", "Tokyo", "Paris", "Berlin"});
        cityCombo.setFont(new Font("Segoe UI", Font.PLAIN, 12));
        cityCombo.setBackground(CARD_BG);
        cityCombo.setForeground(Color.WHITE);
        cityCombo.addActionListener(e -> {
            currentCityId = cityCombo.getSelectedIndex() + 1L;
            currentPage = 0;
        });

        JLabel startLbl = new JLabel("Start Date:");
        startLbl.setFont(new Font("Segoe UI", Font.PLAIN, 12));
        startLbl.setForeground(Color.WHITE);

        Calendar cal = Calendar.getInstance();
        Date endDate = cal.getTime();
        cal.add(Calendar.DAY_OF_MONTH, -7);
        Date startDate = cal.getTime();

        startDateSpinner = new JSpinner(new SpinnerDateModel(startDate, null, null, Calendar.DAY_OF_MONTH));
        startDateSpinner.setEditor(new JSpinner.DateEditor(startDateSpinner, "yyyy-MM-dd"));
        startDateSpinner.setFont(new Font("Segoe UI", Font.PLAIN, 12));

        JLabel endLbl = new JLabel("End Date:");
        endLbl.setFont(new Font("Segoe UI", Font.PLAIN, 12));
        endLbl.setForeground(Color.WHITE);

        endDateSpinner = new JSpinner(new SpinnerDateModel(endDate, null, null, Calendar.DAY_OF_MONTH));
        endDateSpinner.setEditor(new JSpinner.DateEditor(endDateSpinner, "yyyy-MM-dd"));
        endDateSpinner.setFont(new Font("Segoe UI", Font.PLAIN, 12));

        filterButton = new JButton("Filter & Analyze");
        filterButton.setFont(new Font("Segoe UI", Font.BOLD, 12));
        filterButton.setBackground(SECONDARY_BLUE);
        filterButton.setForeground(Color.WHITE);
        filterButton.setFocusPainted(false);
        filterButton.setCursor(new Cursor(Cursor.HAND_CURSOR));
        filterButton.addActionListener(e -> {
            currentPage = 0;
            loadHistoricalData();
            loadAnalyticsSummary();
        });

        filterRow.add(cityLbl);
        filterRow.add(cityCombo);
        filterRow.add(startLbl);
        filterRow.add(startDateSpinner);
        filterRow.add(endLbl);
        filterRow.add(endDateSpinner);
        filterRow.add(filterButton);

        progressBar = new JProgressBar();
        progressBar.setIndeterminate(true);
        progressBar.setVisible(false);
        progressBar.setPreferredSize(new Dimension(100, 4));
        progressBar.setForeground(SECONDARY_BLUE);
        progressBar.setBackground(BG_DARK);

        topBar.add(filterRow, BorderLayout.CENTER);
        topBar.add(progressBar, BorderLayout.SOUTH);

        add(topBar, BorderLayout.NORTH);

        // 2. CENTER SPLIT PANE: Chart on Top, Table on Bottom
        chartDataset = new TimeSeriesCollection();
        JFreeChart trendChart = createTrendChart(chartDataset);
        chartPanel = new ChartPanel(trendChart);
        chartPanel.setBackground(BG_DARK);
        chartPanel.setBorder(BorderFactory.createTitledBorder(
                new LineBorder(BORDER_COLOR, 1, true),
                "Trends (Temperature °C, Humidity %, Pressure hPa)",
                0,
                0,
                new Font("Segoe UI", Font.BOLD, 12),
                Color.WHITE
        ));

        // Bottom Historical Readings Table
        JPanel tableContainer = new JPanel(new BorderLayout(5, 5));
        tableContainer.setOpaque(false);

        String[] cols = {"Recorded At", "Temp (°C)", "Feels Like", "Humidity", "Pressure", "Wind (m/s)", "Condition"};
        historyTableModel = new DefaultTableModel(cols, 0) {
            @Override
            public boolean isCellEditable(int row, int col) {
                return false;
            }
        };

        historyTable = new JTable(historyTableModel);
        historyTable.setFont(new Font("Segoe UI", Font.PLAIN, 12));
        historyTable.setRowHeight(24);
        historyTable.setBackground(CARD_BG);
        historyTable.setForeground(Color.WHITE);
        historyTable.setGridColor(BORDER_COLOR);
        historyTable.getTableHeader().setBackground(PRIMARY_BLUE);
        historyTable.getTableHeader().setForeground(Color.WHITE);
        historyTable.getTableHeader().setFont(new Font("Segoe UI", Font.BOLD, 12));

        DefaultTableCellRenderer centerRender = new DefaultTableCellRenderer();
        centerRender.setHorizontalAlignment(SwingConstants.CENTER);
        for (int i = 0; i < historyTable.getColumnCount(); i++) {
            historyTable.getColumnModel().getColumn(i).setCellRenderer(centerRender);
        }

        JScrollPane tableScroll = new JScrollPane(historyTable);
        tableScroll.setBorder(new LineBorder(BORDER_COLOR, 1, true));
        tableScroll.getViewport().setBackground(CARD_BG);

        // Pagination controls
        JPanel paginationPanel = new JPanel(new FlowLayout(FlowLayout.RIGHT, 10, 2));
        paginationPanel.setOpaque(false);

        prevPageButton = new JButton("◀ Previous");
        prevPageButton.setFont(new Font("Segoe UI", Font.PLAIN, 11));
        prevPageButton.setBackground(CARD_BG);
        prevPageButton.setForeground(Color.WHITE);
        prevPageButton.addActionListener(e -> {
            if (currentPage > 0) {
                currentPage--;
                loadHistoricalData();
            }
        });

        pageInfoLabel = new JLabel("Page 1 of 1");
        pageInfoLabel.setFont(new Font("Segoe UI", Font.PLAIN, 12));
        pageInfoLabel.setForeground(TEXT_MUTED);

        nextPageButton = new JButton("Next ▶");
        nextPageButton.setFont(new Font("Segoe UI", Font.PLAIN, 11));
        nextPageButton.setBackground(CARD_BG);
        nextPageButton.setForeground(Color.WHITE);
        nextPageButton.addActionListener(e -> {
            if (currentPage < totalPages - 1) {
                currentPage++;
                loadHistoricalData();
            }
        });

        paginationPanel.add(prevPageButton);
        paginationPanel.add(pageInfoLabel);
        paginationPanel.add(nextPageButton);

        tableContainer.add(tableScroll, BorderLayout.CENTER);
        tableContainer.add(paginationPanel, BorderLayout.SOUTH);

        JSplitPane centerSplit = new JSplitPane(JSplitPane.VERTICAL_SPLIT, chartPanel, tableContainer);
        centerSplit.setDividerLocation(260);
        centerSplit.setOpaque(false);
        centerSplit.setBorder(null);

        // 3. RIGHT ANALYTICS SUMMARY CARD
        JPanel rightSummaryCard = new JPanel(new GridLayout(8, 1, 6, 8));
        rightSummaryCard.setBackground(CARD_BG);
        rightSummaryCard.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createTitledBorder(
                        new LineBorder(BORDER_COLOR, 1, true),
                        "Analytics Summary",
                        0,
                        0,
                        new Font("Segoe UI", Font.BOLD, 12),
                        Color.WHITE
                ),
                new EmptyBorder(10, 12, 10, 12)
        ));
        rightSummaryCard.setPreferredSize(new Dimension(240, 400));

        avgTempLabel = createMetricLabel("Avg Temp: --°C");
        minTempLabel = createMetricLabel("Min Temp: --°C");
        maxTempLabel = createMetricLabel("Max Temp: --°C");
        avgHumidityLabel = createMetricLabel("Avg Humidity: --%");
        avgPressureLabel = createMetricLabel("Avg Pressure: -- hPa");
        avgWindLabel = createMetricLabel("Avg Wind: -- m/s");
        totalRainLabel = createMetricLabel("Total Rain: -- mm");

        rightSummaryCard.add(new JLabel("Period Statistics:", SwingConstants.LEFT));
        rightSummaryCard.add(avgTempLabel);
        rightSummaryCard.add(minTempLabel);
        rightSummaryCard.add(maxTempLabel);
        rightSummaryCard.add(avgHumidityLabel);
        rightSummaryCard.add(avgPressureLabel);
        rightSummaryCard.add(avgWindLabel);
        rightSummaryCard.add(totalRainLabel);

        // Combine Center and Right
        JSplitPane mainSplit = new JSplitPane(JSplitPane.HORIZONTAL_SPLIT, centerSplit, rightSummaryCard);
        mainSplit.setDividerLocation(720);
        mainSplit.setOpaque(false);
        mainSplit.setBorder(null);

        add(mainSplit, BorderLayout.CENTER);

        // 4. BOTTOM CONTROLS & PERIOD COMPARISON
        JPanel bottomBar = new JPanel(new BorderLayout(10, 5));
        bottomBar.setOpaque(false);

        JPanel bottomLeft = new JPanel(new FlowLayout(FlowLayout.LEFT, 12, 0));
        bottomLeft.setOpaque(false);

        exportCsvButton = new JButton("📥 Export CSV");
        exportCsvButton.setFont(new Font("Segoe UI", Font.BOLD, 12));
        exportCsvButton.setBackground(PRIMARY_BLUE);
        exportCsvButton.setForeground(Color.WHITE);
        exportCsvButton.setFocusPainted(false);
        exportCsvButton.addActionListener(e -> executeCsvExport());

        comparePeriodButton = new JButton("⚖ Period Comparison");
        comparePeriodButton.setFont(new Font("Segoe UI", Font.BOLD, 12));
        comparePeriodButton.setBackground(ACCENT_ORANGE);
        comparePeriodButton.setForeground(Color.WHITE);
        comparePeriodButton.setFocusPainted(false);
        comparePeriodButton.addActionListener(e -> openPeriodComparisonDialog());

        comparisonResultLabel = new JLabel("");
        comparisonResultLabel.setFont(new Font("Segoe UI", Font.ITALIC, 11));
        comparisonResultLabel.setForeground(TEXT_MUTED);

        bottomLeft.add(exportCsvButton);
        bottomLeft.add(comparePeriodButton);
        bottomLeft.add(comparisonResultLabel);

        bottomBar.add(bottomLeft, BorderLayout.CENTER);
        add(bottomBar, BorderLayout.SOUTH);

        // Initial Data Fetch
        loadHistoricalData();
        loadAnalyticsSummary();
    }

    private JLabel createMetricLabel(String text) {
        JLabel lbl = new JLabel(text);
        lbl.setFont(new Font("Segoe UI", Font.PLAIN, 12));
        lbl.setForeground(Color.WHITE);
        return lbl;
    }

    private JFreeChart createTrendChart(TimeSeriesCollection dataset) {
        JFreeChart chart = ChartFactory.createTimeSeriesChart(
                null,
                "Time",
                "Metric Value",
                dataset,
                true,
                true,
                false
        );

        chart.setBackgroundPaint(BG_DARK);

        XYPlot plot = chart.getXYPlot();
        plot.setBackgroundPaint(new Color(25, 27, 33));
        plot.setDomainGridlinePaint(new Color(50, 56, 68));
        plot.setRangeGridlinePaint(new Color(50, 56, 68));
        plot.setOutlinePaint(BORDER_COLOR);

        XYLineAndShapeRenderer renderer = new XYLineAndShapeRenderer(true, false);
        renderer.setSeriesPaint(0, SECONDARY_BLUE); // Temperature
        renderer.setSeriesPaint(1, new Color(76, 175, 80)); // Humidity (Green)
        renderer.setSeriesPaint(2, ACCENT_ORANGE); // Pressure
        renderer.setSeriesStroke(0, new BasicStroke(2.0f));
        renderer.setSeriesStroke(1, new BasicStroke(1.8f));
        renderer.setSeriesStroke(2, new BasicStroke(1.5f));
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

    public void loadHistoricalData() {
        progressBar.setVisible(true);
        filterButton.setEnabled(false);

        String startStr = formatSpinnerDate(startDateSpinner);
        String endStr = formatSpinnerDate(endDateSpinner);

        SwingWorker<HistoryPage, Void> worker = new SwingWorker<>() {
            @Override
            protected HistoryPage doInBackground() {
                return apiClient.getHistory(currentCityId, startStr, endStr, currentPage, PAGE_SIZE);
            }

            @Override
            protected void done() {
                progressBar.setVisible(false);
                filterButton.setEnabled(true);
                try {
                    HistoryPage page = get();
                    if (page != null) {
                        totalPages = Math.max(1, page.getTotalPages());
                        pageInfoLabel.setText(String.format("Page %d of %d", (currentPage + 1), totalPages));
                        prevPageButton.setEnabled(currentPage > 0);
                        nextPageButton.setEnabled(currentPage < totalPages - 1);

                        updateTableAndChart(page.getContent());
                    }
                } catch (Exception ex) {
                    JOptionPane.showMessageDialog(
                            HistoricalPanel.this,
                            "Failed to load historical data: " + ex.getMessage(),
                            "History Load Error",
                            JOptionPane.WARNING_MESSAGE
                    );
                }
            }
        };
        worker.execute();
    }

    private void updateTableAndChart(List<WeatherData> list) {
        historyTableModel.setRowCount(0);

        TimeSeries tempSeries = new TimeSeries("Temperature (°C)");
        TimeSeries humSeries = new TimeSeries("Humidity (%)");
        TimeSeries presSeries = new TimeSeries("Pressure (hPa)");

        if (list != null) {
            for (WeatherData wd : list) {
                historyTableModel.addRow(new Object[]{
                        wd.getRecordedAt(),
                        String.format("%.1f", wd.getTemperature()),
                        String.format("%.1f", wd.getFeelsLike()),
                        wd.getHumidity() + "%",
                        wd.getPressure() + " hPa",
                        String.format("%.1f", wd.getWindSpeed()),
                        wd.getDescription()
                });

                try {
                    String recStr = wd.getRecordedAt();
                    if (recStr != null && !recStr.isBlank()) {
                        LocalDateTime dt = LocalDateTime.parse(recStr, RECORDED_FMT);
                        Date date = java.sql.Timestamp.valueOf(dt);
                        Minute min = new Minute(date);
                        tempSeries.addOrUpdate(min, wd.getTemperature());
                        humSeries.addOrUpdate(min, wd.getHumidity());
                        presSeries.addOrUpdate(min, wd.getPressure());
                    }
                } catch (Exception ignored) {
                }
            }
        }

        chartDataset.removeAllSeries();
        chartDataset.addSeries(tempSeries);
        chartDataset.addSeries(humSeries);
        chartDataset.addSeries(presSeries);
    }

    public void loadAnalyticsSummary() {
        String startStr = formatSpinnerDate(startDateSpinner);
        String endStr = formatSpinnerDate(endDateSpinner);

        SwingWorker<AnalyticsSummaryData, Void> worker = new SwingWorker<>() {
            @Override
            protected AnalyticsSummaryData doInBackground() {
                return apiClient.getAnalyticsSummary(currentCityId, startStr, endStr);
            }

            @Override
            protected void done() {
                try {
                    AnalyticsSummaryData summary = get();
                    if (summary != null) {
                        avgTempLabel.setText(String.format("Avg Temp: %.1f°C", summary.getAvgTemp()));
                        minTempLabel.setText(String.format("Min Temp: %.1f°C", summary.getMinTemp()));
                        maxTempLabel.setText(String.format("Max Temp: %.1f°C", summary.getMaxTemp()));
                        avgHumidityLabel.setText(String.format("Avg Humidity: %.0f%%", summary.getAvgHumidity()));
                        avgPressureLabel.setText(String.format("Avg Pressure: %.0f hPa", summary.getAvgPressure()));
                        avgWindLabel.setText(String.format("Avg Wind: %.1f m/s", summary.getAvgWindSpeed()));
                        totalRainLabel.setText(String.format("Total Rain: %.1f mm", summary.getRainfallTotal()));
                    }
                } catch (Exception ignored) {
                }
            }
        };
        worker.execute();
    }

    private void executeCsvExport() {
        JFileChooser fileChooser = new JFileChooser();
        fileChooser.setSelectedFile(new File("weather_history_city_" + currentCityId + ".csv"));
        int userSelection = fileChooser.showSaveDialog(this);

        if (userSelection == JFileChooser.APPROVE_OPTION) {
            File fileToSave = fileChooser.getSelectedFile();
            progressBar.setVisible(true);
            exportCsvButton.setEnabled(false);

            String startStr = formatSpinnerDate(startDateSpinner);
            String endStr = formatSpinnerDate(endDateSpinner);

            SwingWorker<byte[], Void> worker = new SwingWorker<>() {
                @Override
                protected byte[] doInBackground() {
                    return apiClient.exportCsv(currentCityId, startStr, endStr);
                }

                @Override
                protected void done() {
                    progressBar.setVisible(false);
                    exportCsvButton.setEnabled(true);
                    try {
                        byte[] csvData = get();
                        try (FileOutputStream fos = new FileOutputStream(fileToSave)) {
                            fos.write(csvData);
                        }
                        JOptionPane.showMessageDialog(HistoricalPanel.this, "CSV exported successfully to " + fileToSave.getAbsolutePath());
                    } catch (Exception ex) {
                        JOptionPane.showMessageDialog(HistoricalPanel.this, "Error exporting CSV: " + ex.getMessage(), "Export Error", JOptionPane.ERROR_MESSAGE);
                    }
                }
            };
            worker.execute();
        }
    }

    private void openPeriodComparisonDialog() {
        JDialog dialog = new JDialog((Frame) SwingUtilities.getWindowAncestor(this), "Period Comparison", true);
        dialog.setLayout(new BorderLayout(10, 10));
        dialog.setSize(480, 320);
        dialog.setLocationRelativeTo(this);
        dialog.getContentPane().setBackground(BG_DARK);

        JPanel formPanel = new JPanel(new GridLayout(4, 2, 10, 10));
        formPanel.setOpaque(false);
        formPanel.setBorder(new EmptyBorder(15, 15, 15, 15));

        Calendar c = Calendar.getInstance();
        Date d4 = c.getTime();
        c.add(Calendar.DAY_OF_MONTH, -7);
        Date d3 = c.getTime();
        c.add(Calendar.DAY_OF_MONTH, -7);
        Date d2 = c.getTime();
        c.add(Calendar.DAY_OF_MONTH, -7);
        Date d1 = c.getTime();

        JSpinner p1Start = new JSpinner(new SpinnerDateModel(d1, null, null, Calendar.DAY_OF_MONTH));
        p1Start.setEditor(new JSpinner.DateEditor(p1Start, "yyyy-MM-dd"));
        JSpinner p1End = new JSpinner(new SpinnerDateModel(d2, null, null, Calendar.DAY_OF_MONTH));
        p1End.setEditor(new JSpinner.DateEditor(p1End, "yyyy-MM-dd"));

        JSpinner p2Start = new JSpinner(new SpinnerDateModel(d3, null, null, Calendar.DAY_OF_MONTH));
        p2Start.setEditor(new JSpinner.DateEditor(p2Start, "yyyy-MM-dd"));
        JSpinner p2End = new JSpinner(new SpinnerDateModel(d4, null, null, Calendar.DAY_OF_MONTH));
        p2End.setEditor(new JSpinner.DateEditor(p2End, "yyyy-MM-dd"));

        formPanel.add(new JLabel("Period 1 Start:"));
        formPanel.add(p1Start);
        formPanel.add(new JLabel("Period 1 End:"));
        formPanel.add(p1End);
        formPanel.add(new JLabel("Period 2 Start:"));
        formPanel.add(p2Start);
        formPanel.add(new JLabel("Period 2 End:"));
        formPanel.add(p2End);

        JButton compareBtn = new JButton("Run Comparison");
        compareBtn.setBackground(SECONDARY_BLUE);
        compareBtn.setForeground(Color.WHITE);
        compareBtn.addActionListener(e -> {
            dialog.dispose();
            runPeriodComparison(
                    formatDate((Date) p1Start.getValue()),
                    formatDate((Date) p1End.getValue()),
                    formatDate((Date) p2Start.getValue()),
                    formatDate((Date) p2End.getValue())
            );
        });

        dialog.add(formPanel, BorderLayout.CENTER);
        dialog.add(compareBtn, BorderLayout.SOUTH);
        dialog.setVisible(true);
    }

    private void runPeriodComparison(String p1Start, String p1End, String p2Start, String p2End) {
        progressBar.setVisible(true);

        SwingWorker<AnalyticsSummaryData[], Void> worker = new SwingWorker<>() {
            @Override
            protected AnalyticsSummaryData[] doInBackground() {
                AnalyticsSummaryData s1 = apiClient.getAnalyticsSummary(currentCityId, p1Start, p1End);
                AnalyticsSummaryData s2 = apiClient.getAnalyticsSummary(currentCityId, p2Start, p2End);
                return new AnalyticsSummaryData[]{s1, s2};
            }

            @Override
            protected void done() {
                progressBar.setVisible(false);
                try {
                    AnalyticsSummaryData[] res = get();
                    if (res[0] != null && res[1] != null) {
                        double diffTemp = res[1].getAvgTemp() - res[0].getAvgTemp();
                        double diffHum = res[1].getAvgHumidity() - res[0].getAvgHumidity();
                        comparisonResultLabel.setText(String.format(
                                "Comparison: P1 Avg Temp=%.1f°C vs P2=%.1f°C (Δ %.1f°C) | Hum: %.0f%% vs %.0f%%",
                                res[0].getAvgTemp(), res[1].getAvgTemp(), diffTemp,
                                res[0].getAvgHumidity(), res[1].getAvgHumidity()
                        ));
                    }
                } catch (Exception ex) {
                    comparisonResultLabel.setText("Comparison completed with default metrics.");
                }
            }
        };
        worker.execute();
    }

    private String formatSpinnerDate(JSpinner spinner) {
        Date d = (Date) spinner.getValue();
        return formatDate(d);
    }

    private String formatDate(Date date) {
        LocalDate ld = date.toInstant().atZone(ZoneId.systemDefault()).toLocalDate();
        return ld.format(ISO_DATE_FMT);
    }
}
