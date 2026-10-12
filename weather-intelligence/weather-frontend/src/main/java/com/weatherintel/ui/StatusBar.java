package com.weatherintel.ui;

import javax.swing.*;
import javax.swing.border.EmptyBorder;
import java.awt.*;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

/**
 * Status bar displayed at the bottom of the application window.
 * Shows connection status indicator, last update timestamp, notification badge, and server URL.
 */
public class StatusBar extends JPanel {

    private static final DateTimeFormatter TIME_FORMATTER = DateTimeFormatter.ofPattern("HH:mm:ss");

    private final JLabel statusDotLabel;
    private final JLabel statusTextLabel;
    private final JLabel lastUpdateLabel;
    private final JLabel notificationBadgeLabel;
    private final JLabel serverUrlLabel;

    private boolean isConnected = false;
    private int notificationCount = 0;
    private String serverUrl = "http://localhost:8080";

    public StatusBar() {
        this("http://localhost:8080");
    }

    public StatusBar(String initialServerUrl) {
        if (initialServerUrl != null && !initialServerUrl.isBlank()) {
            this.serverUrl = initialServerUrl;
        }

        setLayout(new BoxLayout(this, BoxLayout.X_AXIS));
        setBorder(new EmptyBorder(6, 12, 6, 12));
        setBackground(new Color(24, 27, 33));

        // Connection status indicator
        statusDotLabel = new JLabel("●");
        statusDotLabel.setFont(new Font("Segoe UI", Font.BOLD, 14));
        statusDotLabel.setForeground(new Color(220, 53, 69)); // red default

        statusTextLabel = new JLabel(" Disconnected");
        statusTextLabel.setFont(new Font("Segoe UI", Font.PLAIN, 12));
        statusTextLabel.setForeground(new Color(180, 185, 195));

        // Last updated time label
        lastUpdateLabel = new JLabel("Last updated: Never");
        lastUpdateLabel.setFont(new Font("Segoe UI", Font.PLAIN, 12));
        lastUpdateLabel.setForeground(new Color(160, 165, 175));

        // Notification count badge
        notificationBadgeLabel = new JLabel(" \uD83D\uDD14 0 ");
        notificationBadgeLabel.setFont(new Font("Segoe UI", Font.BOLD, 12));
        notificationBadgeLabel.setOpaque(true);
        notificationBadgeLabel.setBackground(new Color(45, 52, 65));
        notificationBadgeLabel.setForeground(Color.WHITE);
        notificationBadgeLabel.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createLineBorder(new Color(70, 80, 95), 1, true),
                BorderFactory.createEmptyBorder(2, 6, 2, 6)
        ));

        // Server URL label
        serverUrlLabel = new JLabel("Server: " + this.serverUrl);
        serverUrlLabel.setFont(new Font("Segoe UI", Font.PLAIN, 12));
        serverUrlLabel.setForeground(new Color(130, 138, 150));

        // Assemble components horizontally
        add(statusDotLabel);
        add(statusTextLabel);
        add(Box.createHorizontalStrut(20));
        add(createSeparator());
        add(Box.createHorizontalStrut(20));
        add(lastUpdateLabel);
        add(Box.createHorizontalGlue());
        add(notificationBadgeLabel);
        add(Box.createHorizontalStrut(20));
        add(createSeparator());
        add(Box.createHorizontalStrut(20));
        add(serverUrlLabel);
    }

    private JComponent createSeparator() {
        JSeparator sep = new JSeparator(SwingConstants.VERTICAL);
        sep.setMaximumSize(new Dimension(2, 16));
        sep.setForeground(new Color(60, 68, 80));
        return sep;
    }

    public void setConnected(boolean connected) {
        SwingUtilities.invokeLater(() -> {
            this.isConnected = connected;
            if (connected) {
                statusDotLabel.setForeground(new Color(40, 167, 69)); // green
                statusTextLabel.setText(" Connected");
            } else {
                statusDotLabel.setForeground(new Color(220, 53, 69)); // red
                statusTextLabel.setText(" Disconnected");
            }
        });
    }

    public boolean isConnected() {
        return isConnected;
    }

    public void setLastUpdated(LocalDateTime timestamp) {
        if (timestamp != null) {
            setLastUpdated(timestamp.format(TIME_FORMATTER));
        }
    }

    public void setLastUpdated(String timeText) {
        SwingUtilities.invokeLater(() -> {
            lastUpdateLabel.setText("Last updated: " + (timeText != null ? timeText : "Never"));
        });
    }

    public void setNotificationCount(int count) {
        SwingUtilities.invokeLater(() -> {
            this.notificationCount = count;
            notificationBadgeLabel.setText(" \uD83D\uDD14 " + count + " ");
            if (count > 0) {
                notificationBadgeLabel.setBackground(new Color(217, 83, 79)); // highlight when there are unread notifications
                notificationBadgeLabel.setForeground(Color.WHITE);
            } else {
                notificationBadgeLabel.setBackground(new Color(45, 52, 65));
                notificationBadgeLabel.setForeground(new Color(180, 185, 195));
            }
        });
    }

    public int getNotificationCount() {
        return notificationCount;
    }

    public void setServerUrl(String url) {
        SwingUtilities.invokeLater(() -> {
            this.serverUrl = url;
            serverUrlLabel.setText("Server: " + (url != null ? url : "Unknown"));
        });
    }

    public String getServerUrl() {
        return serverUrl;
    }
}
