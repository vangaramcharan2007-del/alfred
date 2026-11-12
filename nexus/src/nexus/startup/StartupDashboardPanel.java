package nexus.startup;

import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import nexus.common.NexusEvent;
import nexus.common.NexusListener;
import nexus.common.EventBus;
import nexus.tasks.Task;
import nexus.tasks.TaskPriority;

public class StartupDashboardPanel extends JPanel implements NexusListener {
    private double currentBudget = 0.0;
    private int raidBossHealth = 10000;
    private JPanel visaCardPanel;
    private JProgressBar healthBar;
    private JButton bossButton;

    public StartupDashboardPanel() {
        setLayout(new GridLayout(3, 1, 10, 10));

        // Section 1: FinTech Visa Card
        visaCardPanel = new JPanel() {
            @Override
            protected void paintComponent(Graphics g) {
                super.paintComponent(g);
                Graphics2D g2 = (Graphics2D) g;
                g2.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
                g2.setColor(new Color(30, 30, 30));
                g2.fillRoundRect(10, 10, getWidth() - 20, getHeight() - 20, 20, 20);
                
                g2.setColor(Color.WHITE);
                g2.setFont(new Font("Arial", Font.BOLD, 24));
                g2.drawString("NEXUS VISA", 30, 50);

                if (currentBudget <= 0) {
                    g2.setColor(Color.RED);
                    g2.setFont(new Font("Arial", Font.BOLD, 48));
                    g2.drawString("CARD LOCKED", getWidth() / 2 - 170, getHeight() / 2 + 20);
                } else {
                    g2.setColor(Color.GREEN);
                    g2.setFont(new Font("Arial", Font.BOLD, 24));
                    g2.drawString("ACTIVE", 30, getHeight() - 30);
                }
            }
        };
        add(visaCardPanel);

        // Section 2: Corporate B2B Sync
        JPanel b2bPanel = new JPanel();
        b2bPanel.add(new JLabel("Corporate Enterprise Integration"));
        JButton syncButton = new JButton("Sync Jira Tickets");
        syncButton.addActionListener(e -> {
            EventBus.getInstance().publish(new NexusEvent("TASK_COMPLETED", new Task("JIRA-841: Fix Production Bug", TaskPriority.HIGH), "Startup"));
        });
        b2bPanel.add(syncButton);
        add(b2bPanel);

        // Section 3: Multiplayer Guild Boss
        JPanel bossPanel = new JPanel(new BorderLayout());
        healthBar = new JProgressBar(0, 10000);
        healthBar.setValue(raidBossHealth);
        healthBar.setForeground(Color.RED);
        healthBar.setStringPainted(true);
        healthBar.setString("Raid Boss Health");
        
        bossButton = new JButton("Simulate Friend Completing Task");
        bossButton.addActionListener(e -> {
            raidBossHealth -= 500;
            if (raidBossHealth <= 0) {
                raidBossHealth = 0;
                healthBar.setValue(0);
                healthBar.setString("BOSS DEFEATED! +1000 XP to Guild");
                bossButton.setEnabled(false);
            } else {
                healthBar.setValue(raidBossHealth);
            }
        });

        bossPanel.add(healthBar, BorderLayout.CENTER);
        bossPanel.add(bossButton, BorderLayout.SOUTH);
        add(bossPanel);

        EventBus.getInstance().subscribeToAll(this);
    }

    @Override
    public void onEvent(NexusEvent event) {
        if ("BUDGET_UPDATED".equals(event.getType())) {
            if (event.getPayload() instanceof Double) {
                currentBudget = (Double) event.getPayload();
            } else if (event.getPayload() instanceof Float) {
                currentBudget = ((Float) event.getPayload()).doubleValue();
            } else if (event.getPayload() instanceof Integer) {
                currentBudget = ((Integer) event.getPayload()).doubleValue();
            } else if (event.getPayload() instanceof String) {
                try {
                    currentBudget = Double.parseDouble((String) event.getPayload());
                } catch (Exception e) {}
            }
            visaCardPanel.repaint();
        }
    }
}
