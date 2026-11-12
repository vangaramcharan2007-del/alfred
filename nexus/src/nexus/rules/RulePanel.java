package nexus.rules;

import javax.swing.*;
import java.awt.*;
import nexus.common.EventBus;
import nexus.common.NexusEvent;

public class RulePanel extends JPanel {
    public RulePanel(RuleEngineService ruleEngine) {
        setLayout(new BorderLayout());
        setBorder(BorderFactory.createEmptyBorder(20, 20, 20, 20));
        
        JLabel title = new JLabel("Rule Builder");
        title.setFont(new Font("Arial", Font.BOLD, 24));
        add(title, BorderLayout.NORTH);
        
        JPanel formPanel = new JPanel(new GridLayout(4, 2, 10, 10));
        formPanel.add(new JLabel("IF Event:"));
        JComboBox<String> ifDropdown = new JComboBox<>(new String[]{"TASK_COMPLETED", "PRODUCT_PURCHASED", "GOAL_COMPLETED"});
        formPanel.add(ifDropdown);
        
        formPanel.add(new JLabel("THEN Action:"));
        JComboBox<String> thenDropdown = new JComboBox<>(new String[]{"Add $5 Budget", "Increase Score by 10", "Show Notification"});
        formPanel.add(thenDropdown);
        
        JButton saveBtn = new JButton("Save Rule");
        saveBtn.addActionListener(e -> {
            String event = (String) ifDropdown.getSelectedItem();
            String action = (String) thenDropdown.getSelectedItem();
            
            ruleEngine.addRule(event, ev -> {
                SwingUtilities.invokeLater(() -> {
                    if ("Add $5 Budget".equals(action)) {
                        EventBus.getInstance().publish(new NexusEvent("ADD_FUNDS_REQUEST", 5.0, "RuleEngine"));
                    } else if ("Increase Score by 10".equals(action)) {
                        EventBus.getInstance().publish(new NexusEvent("ADD_SCORE_REQUEST", 10, "RuleEngine"));
                    } else if ("Show Notification".equals(action)) {
                        EventBus.getInstance().publish(new NexusEvent("NOTIFICATION", "Custom Rule Triggered by " + event, "RuleEngine"));
                    }
                });
            });
            JOptionPane.showMessageDialog(this, "Rule saved successfully!");
        });
        
        formPanel.add(new JLabel("")); // Spacer
        formPanel.add(saveBtn);
        
        add(formPanel, BorderLayout.CENTER);
    }
}
