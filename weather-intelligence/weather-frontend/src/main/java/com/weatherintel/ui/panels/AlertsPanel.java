package com.weatherintel.ui.panels;

import com.weatherintel.ui.services.ApiClient;
import com.weatherintel.ui.services.ApiClient.AlertData;
import com.weatherintel.ui.services.ApiClient.NotificationData;

import javax.swing.*;
import javax.swing.border.EmptyBorder;
import javax.swing.border.LineBorder;
import javax.swing.table.DefaultTableCellRenderer;
import javax.swing.table.DefaultTableModel;
import java.awt.*;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ExecutionException;

/**
 * Alerts and notifications management panel.
 * Allows creating, listing, toggling, and deleting weather alert rules,
 * and reviewing live notification triggers with unread status indicators.
 */
public class AlertsPanel extends JPanel {

    private static final Color BG_DARK = new Color(0x1E, 0x1E, 0x1E);
    private static final Color CARD_BG = new Color(0x2D, 0x2D, 0x2D);
    private static final Color PRIMARY_BLUE = new Color(0x1E, 0x3E, 0x72);
    private static final Color SECONDARY_BLUE = new Color(0x21, 0x96, 0xF3);
    private static final Color ACCENT_ORANGE = new Color(0xFF, 0x98, 0x00);
    private static final Color TEXT_MUTED = new Color(170, 175, 185);
    private static final Color BORDER_COLOR = new Color(60, 65, 75);

    private static final long DEFAULT_USER_ID = 1L;

    private final ApiClient apiClient;

    // Top Controls
    private final JButton createAlertButton;
    private final JButton deleteAlertButton;
    private final JButton refreshAlertsButton;
    private final JLabel notificationBadge;
    private final JProgressBar progressBar;

    // Center Alerts Table
    private final DefaultTableModel alertsTableModel;
    private final JTable alertsTable;
    private final List<AlertData> currentAlerts = new ArrayList<>();

    // Right Notifications List
    private final DefaultListModel<NotificationData> notificationsListModel;
    private final JList<NotificationData> notificationsList;
    private final JButton markReadButton;
    private final JButton markAllReadButton;

    public AlertsPanel(ApiClient apiClient) {
        this.apiClient = apiClient != null ? apiClient : new ApiClient();

        setLayout(new BorderLayout(15, 15));
        setBackground(BG_DARK);
        setBorder(new EmptyBorder(15, 15, 15, 15));

        // 1. TOP TOOLBAR
        JPanel topBar = new JPanel(new BorderLayout(10, 8));
        topBar.setOpaque(false);

        JPanel leftActions = new JPanel(new FlowLayout(FlowLayout.LEFT, 12, 0));
        leftActions.setOpaque(false);

        createAlertButton = new JButton("+ Create Alert");
        createAlertButton.setFont(new Font("Segoe UI", Font.BOLD, 12));
        createAlertButton.setBackground(SECONDARY_BLUE);
        createAlertButton.setForeground(Color.WHITE);
        createAlertButton.setFocusPainted(false);
        createAlertButton.setCursor(new Cursor(Cursor.HAND_CURSOR));
        createAlertButton.addActionListener(e -> showCreateAlertDialog());

        deleteAlertButton = new JButton("✖ Delete Alert");
        deleteAlertButton.setFont(new Font("Segoe UI", Font.BOLD, 12));
        deleteAlertButton.setBackground(new Color(180, 40, 40));
        deleteAlertButton.setForeground(Color.WHITE);
        deleteAlertButton.setFocusPainted(false);
        deleteAlertButton.addActionListener(e -> deleteSelectedAlert());

        refreshAlertsButton = new JButton("↻ Refresh");
        refreshAlertsButton.setFont(new Font("Segoe UI", Font.BOLD, 12));
        refreshAlertsButton.setBackground(PRIMARY_BLUE);
        refreshAlertsButton.setForeground(Color.WHITE);
        refreshAlertsButton.setFocusPainted(false);
        refreshAlertsButton.addActionListener(e -> {
            loadAlerts();
            loadNotifications();
        });

        leftActions.add(createAlertButton);
        leftActions.add(deleteAlertButton);
        leftActions.add(refreshAlertsButton);

        JPanel rightBadge = new JPanel(new FlowLayout(FlowLayout.RIGHT, 10, 0));
        rightBadge.setOpaque(false);

        notificationBadge = new JLabel(" \uD83D\uDD14 0 Unread ");
        notificationBadge.setFont(new Font("Segoe UI", Font.BOLD, 12));
        notificationBadge.setOpaque(true);
        notificationBadge.setBackground(new Color(45, 52, 65));
        notificationBadge.setForeground(Color.WHITE);
        notificationBadge.setBorder(BorderFactory.createCompoundBorder(
                new LineBorder(BORDER_COLOR, 1, true),
                new EmptyBorder(4, 8, 4, 8)
        ));
        rightBadge.add(notificationBadge);

        progressBar = new JProgressBar();
        progressBar.setIndeterminate(true);
        progressBar.setVisible(false);
        progressBar.setPreferredSize(new Dimension(100, 4));
        progressBar.setForeground(SECONDARY_BLUE);
        progressBar.setBackground(BG_DARK);

        topBar.add(leftActions, BorderLayout.WEST);
        topBar.add(rightBadge, BorderLayout.EAST);
        topBar.add(progressBar, BorderLayout.SOUTH);

        add(topBar, BorderLayout.NORTH);

        // 2. CENTER ALERTS TABLE & RIGHT NOTIFICATIONS SPLIT
        String[] cols = {"ID", "City", "Type", "Metric / Cond", "Threshold", "Status", "Created At"};
        alertsTableModel = new DefaultTableModel(cols, 0) {
            @Override
            public boolean isCellEditable(int row, int col) {
                return false;
            }
        };

        alertsTable = new JTable(alertsTableModel);
        alertsTable.setFont(new Font("Segoe UI", Font.PLAIN, 12));
        alertsTable.setRowHeight(26);
        alertsTable.setBackground(CARD_BG);
        alertsTable.setForeground(Color.WHITE);
        alertsTable.setGridColor(BORDER_COLOR);
        alertsTable.getTableHeader().setBackground(PRIMARY_BLUE);
        alertsTable.getTableHeader().setForeground(Color.WHITE);
        alertsTable.getTableHeader().setFont(new Font("Segoe UI", Font.BOLD, 12));

        DefaultTableCellRenderer centerRender = new DefaultTableCellRenderer();
        centerRender.setHorizontalAlignment(SwingConstants.CENTER);
        for (int i = 0; i < alertsTable.getColumnCount(); i++) {
            alertsTable.getColumnModel().getColumn(i).setCellRenderer(centerRender);
        }

        JScrollPane tableScroll = new JScrollPane(alertsTable);
        tableScroll.setBorder(BorderFactory.createTitledBorder(
                new LineBorder(BORDER_COLOR, 1, true),
                "Active Weather Alerts",
                0,
                0,
                new Font("Segoe UI", Font.BOLD, 12),
                Color.WHITE
        ));
        tableScroll.getViewport().setBackground(CARD_BG);

        // 3. RIGHT NOTIFICATIONS LIST
        JPanel notificationsPanel = new JPanel(new BorderLayout(5, 8));
        notificationsPanel.setOpaque(false);
        notificationsPanel.setPreferredSize(new Dimension(340, 300));
        notificationsPanel.setBorder(BorderFactory.createTitledBorder(
                new LineBorder(BORDER_COLOR, 1, true),
                "Notifications Feed",
                0,
                0,
                new Font("Segoe UI", Font.BOLD, 12),
                Color.WHITE
        ));

        notificationsListModel = new DefaultListModel<>();
        notificationsList = new JList<>(notificationsListModel);
        notificationsList.setBackground(CARD_BG);
        notificationsList.setSelectionMode(ListSelectionModel.SINGLE_SELECTION);
        notificationsList.setCellRenderer(new NotificationCellRenderer());

        JScrollPane notifScroll = new JScrollPane(notificationsList);
        notifScroll.setBorder(null);
        notifScroll.getViewport().setBackground(CARD_BG);

        JPanel notifActions = new JPanel(new FlowLayout(FlowLayout.RIGHT, 8, 4));
        notifActions.setOpaque(false);

        markReadButton = new JButton("Mark as Read");
        markReadButton.setFont(new Font("Segoe UI", Font.PLAIN, 11));
        markReadButton.setBackground(CARD_BG);
        markReadButton.setForeground(Color.WHITE);
        markReadButton.addActionListener(e -> markSelectedNotificationRead());

        markAllReadButton = new JButton("Mark All Read");
        markAllReadButton.setFont(new Font("Segoe UI", Font.PLAIN, 11));
        markAllReadButton.setBackground(CARD_BG);
        markAllReadButton.setForeground(Color.WHITE);
        markAllReadButton.addActionListener(e -> markAllNotificationsRead());

        notifActions.add(markReadButton);
        notifActions.add(markAllReadButton);

        notificationsPanel.add(notifScroll, BorderLayout.CENTER);
        notificationsPanel.add(notifActions, BorderLayout.SOUTH);

        JSplitPane centerSplit = new JSplitPane(JSplitPane.HORIZONTAL_SPLIT, tableScroll, notificationsPanel);
        centerSplit.setDividerLocation(560);
        centerSplit.setOpaque(false);
        centerSplit.setBorder(null);

        add(centerSplit, BorderLayout.CENTER);

        // Initial Data Fetch
        loadAlerts();
        loadNotifications();
    }

    public void loadAlerts() {
        progressBar.setVisible(true);

        SwingWorker<List<AlertData>, Void> worker = new SwingWorker<>() {
            @Override
            protected List<AlertData> doInBackground() {
                return apiClient.getAlerts(DEFAULT_USER_ID);
            }

            @Override
            protected void done() {
                progressBar.setVisible(false);
                try {
                    List<AlertData> alerts = get();
                    currentAlerts.clear();
                    alertsTableModel.setRowCount(0);
                    if (alerts != null) {
                        currentAlerts.addAll(alerts);
                        for (AlertData a : alerts) {
                            alertsTableModel.addRow(new Object[]{
                                    a.getId(),
                                    a.getCityName(),
                                    a.getAlertType(),
                                    a.getMetric() + " " + a.getOperator(),
                                    a.getThreshold(),
                                    a.isActive() ? "ENABLED" : "DISABLED",
                                    a.getCreatedAt()
                            });
                        }
                    }
                } catch (Exception ex) {
                    JOptionPane.showMessageDialog(
                            AlertsPanel.this,
                            "Failed to load alerts: " + ex.getMessage(),
                            "Alerts Error",
                            JOptionPane.WARNING_MESSAGE
                    );
                }
            }
        };
        worker.execute();
    }

    public void loadNotifications() {
        SwingWorker<List<NotificationData>, Void> worker = new SwingWorker<>() {
            @Override
            protected List<NotificationData> doInBackground() {
                return apiClient.getNotifications(DEFAULT_USER_ID);
            }

            @Override
            protected void done() {
                try {
                    List<NotificationData> list = get();
                    notificationsListModel.clear();
                    int unreadCount = 0;
                    if (list != null) {
                        for (NotificationData nd : list) {
                            notificationsListModel.addElement(nd);
                            if (!nd.isRead()) {
                                unreadCount++;
                            }
                        }
                    }
                    updateBadge(unreadCount);
                } catch (Exception ignored) {
                }
            }
        };
        worker.execute();
    }

    private void updateBadge(int unreadCount) {
        notificationBadge.setText(" \uD83D\uDD14 " + unreadCount + " Unread ");
        if (unreadCount > 0) {
            notificationBadge.setBackground(new Color(217, 83, 79));
            notificationBadge.setForeground(Color.WHITE);
        } else {
            notificationBadge.setBackground(new Color(45, 52, 65));
            notificationBadge.setForeground(TEXT_MUTED);
        }
    }

    private void showCreateAlertDialog() {
        JDialog dialog = new JDialog((Frame) SwingUtilities.getWindowAncestor(this), "Create Weather Alert", true);
        dialog.setLayout(new BorderLayout(10, 10));
        dialog.setSize(440, 340);
        dialog.setLocationRelativeTo(this);
        dialog.getContentPane().setBackground(BG_DARK);

        JPanel form = new JPanel(new GridLayout(5, 2, 10, 10));
        form.setOpaque(false);
        form.setBorder(new EmptyBorder(15, 15, 15, 15));

        JComboBox<String> cityCombo = new JComboBox<>(new String[]{"London", "New York", "Tokyo", "Paris", "Berlin"});
        cityCombo.setFont(new Font("Segoe UI", Font.PLAIN, 12));

        String[] alertTypes = {
                "Temp Above",
                "Temp Below",
                "Humidity Above",
                "Wind Above",
                "Weather Condition"
        };
        JComboBox<String> typeCombo = new JComboBox<>(alertTypes);
        typeCombo.setFont(new Font("Segoe UI", Font.PLAIN, 12));

        JTextField thresholdField = new JTextField("30.0");
        thresholdField.setFont(new Font("Segoe UI", Font.PLAIN, 12));

        JCheckBox enabledCheck = new JCheckBox("Enabled", true);
        enabledCheck.setFont(new Font("Segoe UI", Font.PLAIN, 12));
        enabledCheck.setForeground(Color.WHITE);
        enabledCheck.setOpaque(false);

        form.add(new JLabel("City:"));
        form.add(cityCombo);
        form.add(new JLabel("Alert Type:"));
        form.add(typeCombo);
        form.add(new JLabel("Threshold Value:"));
        form.add(thresholdField);
        form.add(new JLabel("Status:"));
        form.add(enabledCheck);

        JButton saveBtn = new JButton("Save Alert");
        saveBtn.setBackground(SECONDARY_BLUE);
        saveBtn.setForeground(Color.WHITE);
        saveBtn.setFont(new Font("Segoe UI", Font.BOLD, 12));
        saveBtn.addActionListener(e -> {
            String selectedCity = (String) cityCombo.getSelectedItem();
            long cityId = cityCombo.getSelectedIndex() + 1L;
            String type = (String) typeCombo.getSelectedItem();
            double thresh = 0;
            try {
                thresh = Double.parseDouble(thresholdField.getText().trim());
            } catch (NumberFormatException ignored) {
            }

            String metric = "temp";
            String operator = ">";
            String backendType = "TEMP_ABOVE";
            if ("Temp Below".equals(type)) {
                metric = "temp";
                operator = "<";
                backendType = "TEMP_BELOW";
            } else if ("Humidity Above".equals(type)) {
                metric = "humidity";
                operator = ">";
                backendType = "HUMIDITY_ABOVE";
            } else if ("Wind Above".equals(type)) {
                metric = "wind_speed";
                operator = ">";
                backendType = "WIND_ABOVE";
            } else if ("Weather Condition".equals(type)) {
                metric = "condition";
                operator = "==";
                backendType = "WEATHER_CONDITION";
            }

            AlertData newAlert = new AlertData(
                    null,
                    DEFAULT_USER_ID,
                    cityId,
                    selectedCity,
                    backendType,
                    metric,
                    operator,
                    thresh,
                    enabledCheck.isSelected(),
                    ""
            );

            dialog.dispose();
            saveAlert(newAlert);
        });

        dialog.add(form, BorderLayout.CENTER);
        dialog.add(saveBtn, BorderLayout.SOUTH);
        dialog.setVisible(true);
    }

    private void saveAlert(AlertData newAlert) {
        progressBar.setVisible(true);

        SwingWorker<Void, Void> worker = new SwingWorker<>() {
            @Override
            protected Void doInBackground() {
                apiClient.createAlert(DEFAULT_USER_ID, newAlert);
                return null;
            }

            @Override
            protected void done() {
                progressBar.setVisible(false);
                JOptionPane.showMessageDialog(AlertsPanel.this, "Alert saved successfully!");
                loadAlerts();
            }
        };
        worker.execute();
    }

    private void deleteSelectedAlert() {
        int selectedRow = alertsTable.getSelectedRow();
        if (selectedRow < 0) {
            JOptionPane.showMessageDialog(this, "Please select an alert from the table to delete.");
            return;
        }

        Long alertId = (Long) alertsTableModel.getValueAt(selectedRow, 0);
        if (alertId == null) return;

        progressBar.setVisible(true);
        SwingWorker<Void, Void> worker = new SwingWorker<>() {
            @Override
            protected Void doInBackground() {
                apiClient.deleteAlert(alertId);
                return null;
            }

            @Override
            protected void done() {
                progressBar.setVisible(false);
                JOptionPane.showMessageDialog(AlertsPanel.this, "Alert deleted.");
                loadAlerts();
            }
        };
        worker.execute();
    }

    private void markSelectedNotificationRead() {
        NotificationData selected = notificationsList.getSelectedValue();
        if (selected == null) return;

        SwingWorker<Void, Void> worker = new SwingWorker<>() {
            @Override
            protected Void doInBackground() {
                if (selected.getId() != null) {
                    apiClient.markNotificationRead(selected.getId());
                }
                return null;
            }

            @Override
            protected void done() {
                loadNotifications();
            }
        };
        worker.execute();
    }

    private void markAllNotificationsRead() {
        SwingWorker<Void, Void> worker = new SwingWorker<>() {
            @Override
            protected Void doInBackground() {
                for (int i = 0; i < notificationsListModel.getSize(); i++) {
                    NotificationData nd = notificationsListModel.get(i);
                    if (!nd.isRead() && nd.getId() != null) {
                        try {
                            apiClient.markNotificationRead(nd.getId());
                        } catch (Exception ignored) {
                        }
                    }
                }
                return null;
            }

            @Override
            protected void done() {
                loadNotifications();
            }
        };
        worker.execute();
    }

    /**
     * Custom renderer for notification list elements with read/unread visual indicator.
     */
    private static class NotificationCellRenderer extends JPanel implements ListCellRenderer<NotificationData> {
        private final JLabel iconLabel = new JLabel();
        private final JLabel titleLabel = new JLabel();
        private final JLabel msgLabel = new JLabel();
        private final JLabel timeLabel = new JLabel();

        public NotificationCellRenderer() {
            setLayout(new BorderLayout(8, 4));
            setBorder(BorderFactory.createCompoundBorder(
                    new LineBorder(BORDER_COLOR, 1, true),
                    new EmptyBorder(6, 8, 6, 8)
            ));

            JPanel textPanel = new JPanel();
            textPanel.setLayout(new BoxLayout(textPanel, BoxLayout.Y_AXIS));
            textPanel.setOpaque(false);

            titleLabel.setFont(new Font("Segoe UI", Font.BOLD, 12));
            msgLabel.setFont(new Font("Segoe UI", Font.PLAIN, 11));
            timeLabel.setFont(new Font("Segoe UI", Font.ITALIC, 10));
            timeLabel.setForeground(TEXT_MUTED);

            textPanel.add(titleLabel);
            textPanel.add(msgLabel);
            textPanel.add(timeLabel);

            add(iconLabel, BorderLayout.WEST);
            add(textPanel, BorderLayout.CENTER);
        }

        @Override
        public Component getListCellRendererComponent(JList<? extends NotificationData> list,
                                                      NotificationData value, int index,
                                                      boolean isSelected, boolean cellHasFocus) {
            if (value != null) {
                titleLabel.setText(value.getTitle());
                msgLabel.setText(value.getMessage());
                timeLabel.setText(value.getCreatedAt());

                if (value.isRead()) {
                    iconLabel.setText("⚪");
                    setBackground(new Color(38, 42, 50));
                    titleLabel.setForeground(TEXT_MUTED);
                    msgLabel.setForeground(TEXT_MUTED);
                } else {
                    iconLabel.setText("🔴");
                    setBackground(new Color(48, 54, 68));
                    titleLabel.setForeground(Color.WHITE);
                    msgLabel.setForeground(new Color(220, 230, 245));
                }
            }
            return this;
        }
    }
}
