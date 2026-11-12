package nexus.cloud;

import nexus.common.EventBus;
import nexus.common.NexusEvent;
import nexus.common.NexusListener;

import javax.swing.*;
import java.awt.*;
import java.util.List;

public class CloudMeshPanel extends JPanel implements NexusListener {
    private final CloudMeshService service = CloudMeshService.getInstance();
    private final JPanel servicesCardsPanel;
    private final JTextArea kafkaLogArea;
    private final JLabel totalProcessedLabel;
    private final JLabel throughputLabel;
    private String currentTopicFilter = "ALL";

    public CloudMeshPanel() {
        setLayout(new BorderLayout(10, 10));
        setBackground(new Color(15, 23, 42));
        setBorder(BorderFactory.createEmptyBorder(12, 12, 12, 12));

        // 1. TOP HEADER & MICROSERVICES HEALTH CARDS
        JPanel topContainer = new JPanel(new BorderLayout(0, 10));
        topContainer.setOpaque(false);

        JPanel headerBar = new JPanel(new BorderLayout());
        headerBar.setBackground(new Color(30, 41, 59));
        headerBar.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createLineBorder(new Color(51, 65, 85)),
                BorderFactory.createEmptyBorder(8, 14, 8, 14)
        ));

        JLabel title = new JLabel("⚡ DISTRIBUTED CLOUD MICROSERVICES & EVENT MESH (PHASE 8)");
        title.setFont(new Font("Consolas", Font.BOLD, 15));
        title.setForeground(new Color(56, 189, 248));

        JLabel clusterStatus = new JLabel("● CLOUD CLUSTER: HEALTHY (5/5 ONLINE)");
        clusterStatus.setFont(new Font("Segoe UI", Font.BOLD, 12));
        clusterStatus.setForeground(new Color(52, 211, 153));

        headerBar.add(title, BorderLayout.WEST);
        headerBar.add(clusterStatus, BorderLayout.EAST);
        topContainer.add(headerBar, BorderLayout.NORTH);

        // 5 Microservice Health Cards
        servicesCardsPanel = new JPanel(new GridLayout(1, 5, 10, 0));
        servicesCardsPanel.setOpaque(false);
        renderServiceCards();
        topContainer.add(servicesCardsPanel, BorderLayout.CENTER);

        add(topContainer, BorderLayout.NORTH);

        // 2. CENTER KAFKA STREAM TERMINAL
        JPanel centerPanel = new JPanel(new BorderLayout(0, 6));
        centerPanel.setOpaque(false);

        JPanel filterBar = new JPanel(new FlowLayout(FlowLayout.LEFT, 8, 4));
        filterBar.setOpaque(false);

        JLabel filterLabel = new JLabel("Kafka Topic Streams:");
        filterLabel.setFont(new Font("Segoe UI", Font.BOLD, 12));
        filterLabel.setForeground(Color.WHITE);
        filterBar.add(filterLabel);

        filterBar.add(createTopicFilterBtn("ALL"));
        filterBar.add(createTopicFilterBtn("nexus.orders.placed"));
        filterBar.add(createTopicFilterBtn("nexus.tickets.reserved"));
        filterBar.add(createTopicFilterBtn("nexus.seats.locked"));
        filterBar.add(createTopicFilterBtn("nexus.ledger.tx"));

        centerPanel.add(filterBar, BorderLayout.NORTH);

        kafkaLogArea = new JTextArea();
        kafkaLogArea.setEditable(false);
        kafkaLogArea.setFont(new Font("Consolas", Font.PLAIN, 12));
        kafkaLogArea.setBackground(new Color(10, 15, 30));
        kafkaLogArea.setForeground(new Color(0, 255, 200));
        kafkaLogArea.setCaretColor(new Color(0, 255, 200));

        JScrollPane scroll = new JScrollPane(kafkaLogArea);
        scroll.setBorder(BorderFactory.createLineBorder(new Color(51, 65, 85)));
        scroll.getVerticalScrollBar().setUnitIncrement(16);
        centerPanel.add(scroll, BorderLayout.CENTER);

        add(centerPanel, BorderLayout.CENTER);

        // 3. BOTTOM HUD & SPIKE INJECTOR
        JPanel bottomBar = new JPanel(new BorderLayout(10, 0));
        bottomBar.setBackground(new Color(30, 41, 59));
        bottomBar.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createLineBorder(new Color(51, 65, 85)),
                BorderFactory.createEmptyBorder(10, 14, 10, 14)
        ));

        JPanel statsPanel = new JPanel(new FlowLayout(FlowLayout.LEFT, 18, 0));
        statsPanel.setOpaque(false);

        totalProcessedLabel = new JLabel("Processed: 38,491 events");
        totalProcessedLabel.setFont(new Font("Consolas", Font.BOLD, 12));
        totalProcessedLabel.setForeground(Color.WHITE);

        throughputLabel = new JLabel("Cluster Throughput: ~1,420 msgs/sec");
        throughputLabel.setFont(new Font("Consolas", Font.BOLD, 12));
        throughputLabel.setForeground(new Color(52, 211, 153));

        JLabel lagLabel = new JLabel("Consumer Lag: 0 msgs (Real-time)");
        lagLabel.setFont(new Font("Consolas", Font.BOLD, 12));
        lagLabel.setForeground(new Color(56, 189, 248));

        statsPanel.add(totalProcessedLabel);
        statsPanel.add(throughputLabel);
        statsPanel.add(lagLabel);

        JButton burstBtn = new JButton("⚡ Inject 100 Burst Spike Events");
        burstBtn.setFont(new Font("Segoe UI", Font.BOLD, 11));
        burstBtn.setBackground(new Color(245, 158, 11));
        burstBtn.setForeground(Color.BLACK);
        burstBtn.setFocusPainted(false);
        burstBtn.setCursor(new Cursor(Cursor.HAND_CURSOR));
        burstBtn.addActionListener(e -> {
            burstBtn.setEnabled(false);
            burstBtn.setText("⚡ Ingesting Spike Load...");
            service.injectSpikeTraffic(100);
            Timer t = new Timer(1200, ev -> {
                burstBtn.setEnabled(true);
                burstBtn.setText("⚡ Inject 100 Burst Spike Events");
            });
            t.setRepeats(false);
            t.start();
        });

        bottomBar.add(statsPanel, BorderLayout.WEST);
        bottomBar.add(burstBtn, BorderLayout.EAST);
        add(bottomBar, BorderLayout.SOUTH);

        // Subscribe to events
        EventBus.getInstance().subscribe("CLOUD_MESH_TELEMETRY", this);
        EventBus.getInstance().subscribe("KAFKA_MESSAGE_PUBLISHED", this);

        refreshLog();
    }

    private JButton createTopicFilterBtn(String topic) {
        JButton btn = new JButton(topic);
        btn.setFont(new Font("Segoe UI", Font.PLAIN, 10));
        btn.setBackground(topic.equals(currentTopicFilter) ? new Color(59, 130, 246) : new Color(30, 41, 59));
        btn.setForeground(Color.WHITE);
        btn.setFocusPainted(false);
        btn.addActionListener(e -> {
            currentTopicFilter = topic;
            refreshLog();
        });
        return btn;
    }

    private void renderServiceCards() {
        servicesCardsPanel.removeAll();
        for (CloudServiceInfo s : service.getServices()) {
            JPanel card = new JPanel();
            card.setLayout(new BoxLayout(card, BoxLayout.Y_AXIS));
            card.setBackground(new Color(30, 41, 59));
            card.setBorder(BorderFactory.createCompoundBorder(
                    BorderFactory.createMatteBorder(0, 3, 0, 0, new Color(16, 185, 129)),
                    BorderFactory.createEmptyBorder(8, 10, 8, 10)
            ));

            JLabel name = new JLabel(s.getName());
            name.setFont(new Font("Segoe UI", Font.BOLD, 11));
            name.setForeground(Color.WHITE);

            JLabel port = new JLabel("Port " + s.getPort() + " • " + s.getProtocol());
            port.setFont(new Font("Segoe UI", Font.PLAIN, 10));
            port.setForeground(new Color(148, 163, 184));

            JLabel status = new JLabel("● " + s.getStatus() + " (" + s.getLatencyMs() + "ms)");
            status.setFont(new Font("Consolas", Font.BOLD, 11));
            status.setForeground(new Color(52, 211, 153));

            JLabel uptime = new JLabel(s.getUptimePercent() + "% SLA Uptime");
            uptime.setFont(new Font("Segoe UI", Font.ITALIC, 9));
            uptime.setForeground(new Color(56, 189, 248));

            card.add(name);
            card.add(Box.createVerticalStrut(2));
            card.add(port);
            card.add(Box.createVerticalStrut(2));
            card.add(status);
            card.add(Box.createVerticalStrut(2));
            card.add(uptime);

            servicesCardsPanel.add(card);
        }
        servicesCardsPanel.revalidate();
        servicesCardsPanel.repaint();
    }

    private void refreshLog() {
        StringBuilder sb = new StringBuilder();
        List<KafkaMessage> msgs = service.getMessageStream();
        for (KafkaMessage m : msgs) {
            if ("ALL".equals(currentTopicFilter) || m.getTopic().equalsIgnoreCase(currentTopicFilter)) {
                sb.append(m.toString()).append("\n");
            }
        }
        kafkaLogArea.setText(sb.toString());
        kafkaLogArea.setCaretPosition(0);
        totalProcessedLabel.setText("Processed: " + String.format("%,d", service.getTotalEventsProcessed()) + " events");
    }

    @Override
    public void onEvent(NexusEvent event) {
        SwingUtilities.invokeLater(() -> {
            if ("CLOUD_MESH_TELEMETRY".equals(event.getType())) {
                renderServiceCards();
                totalProcessedLabel.setText("Processed: " + String.format("%,d", service.getTotalEventsProcessed()) + " events");
            } else if ("KAFKA_MESSAGE_PUBLISHED".equals(event.getType())) {
                refreshLog();
            }
        });
    }
}