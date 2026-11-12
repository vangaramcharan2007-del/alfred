package nexus.common;

import javax.swing.*;
import java.awt.*;
import java.time.LocalTime;
import java.time.format.DateTimeFormatter;

public class ActivityFeedPanel extends JPanel implements NexusListener {
    private JTextArea feedArea;

    public ActivityFeedPanel() {
        setLayout(new BorderLayout());
        setPreferredSize(new Dimension(250, 0));
        setBorder(BorderFactory.createTitledBorder("Live Activity Feed"));

        feedArea = new JTextArea();
        feedArea.setEditable(false);
        feedArea.setLineWrap(true);
        feedArea.setWrapStyleWord(true);
        feedArea.setFont(new Font("Segoe UI", Font.PLAIN, 12));

        JScrollPane scrollPane = new JScrollPane(feedArea);
        add(scrollPane, BorderLayout.CENTER);

        // Subscribe to interesting events
        EventBus.getInstance().subscribe("TASK_COMPLETED", this);
        EventBus.getInstance().subscribe("GOAL_COMPLETED", this);
        EventBus.getInstance().subscribe("PRODUCT_PURCHASED", this);
        EventBus.getInstance().subscribe("MEDIA_COMPLETED", this);
        EventBus.getInstance().subscribe("MEDIA_ADDED", this);
        EventBus.getInstance().subscribe("INSIGHT_GENERATED", this);
        EventBus.getInstance().subscribe("USER_SWITCHED", this);
        EventBus.getInstance().subscribe("TICKET_BOOKED", this);
    }

    private void logEvent(String message) {
        String time = LocalTime.now().format(DateTimeFormatter.ofPattern("HH:mm"));
        SwingUtilities.invokeLater(() -> {
            feedArea.append("[" + time + "] " + message + "\n\n");
            feedArea.setCaretPosition(feedArea.getDocument().getLength());
        });
    }

    @Override
    public void onEvent(NexusEvent event) {
        String type = event.getType();
        
        if ("TASK_COMPLETED".equals(type)) {
            nexus.tasks.Task t = (nexus.tasks.Task) event.getPayload();
            logEvent("Task Completed: " + t.getTitle());
        } else if ("GOAL_COMPLETED".equals(type)) {
            nexus.goals.Goal g = (nexus.goals.Goal) event.getPayload();
            logEvent("Goal Achieved! " + g.getTitle() + " (Rewarded +$150)");
        } else if ("PRODUCT_PURCHASED".equals(type)) {
            logEvent("Market Purchase: $" + event.getPayload());
        } else if ("MEDIA_COMPLETED".equals(type)) {
            nexus.media.MediaItem m = (nexus.media.MediaItem) event.getPayload();
            logEvent("Media Finished: " + m.getTitle());
        } else if ("MEDIA_ADDED".equals(type)) {
            nexus.media.MediaItem m = (nexus.media.MediaItem) event.getPayload();
            logEvent("New Media Added: " + m.getTitle());
        } else if ("INSIGHT_GENERATED".equals(type)) {
            // Insights are lists, let's just grab the last one
            java.util.List<?> insights = (java.util.List<?>) event.getPayload();
            if (!insights.isEmpty()) {
                nexus.analytics.Insight insight = (nexus.analytics.Insight) insights.get(insights.size() - 1);
                logEvent("Insight: " + insight.getMessage());
            }
        } else if ("USER_SWITCHED".equals(type)) {
            nexus.auth.UserProfile p = (nexus.auth.UserProfile) event.getPayload();
            logEvent("Active Profile: " + p.getAvatar() + " " + p.getName() + " (" + p.getRole() + ")");
        } else if ("TICKET_BOOKED".equals(type)) {
            nexus.media.CinemaBooking b = (nexus.media.CinemaBooking) event.getPayload();
            logEvent("🎟️ Ticket Booked: " + b.getMovieTitle() + " Seats: " + b.getSeatsFormatted() + " Paid via: " + b.getPaymentMethod());
        }
    }
}
