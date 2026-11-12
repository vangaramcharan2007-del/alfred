package nexus.goals;

import javax.swing.*;
import java.awt.*;
import java.util.List;
import nexus.common.EventBus;
import nexus.common.NexusEvent;
import nexus.common.NexusListener;

public class GoalPanel extends JPanel implements NexusListener {
    private final GoalService service;
    private JPanel goalsContainer;
    private JLabel summaryLabel;

    public GoalPanel(GoalService service) {
        this.service = service;
        setLayout(new BorderLayout(15, 15));
        setBorder(BorderFactory.createEmptyBorder(15, 15, 15, 15));
        setBackground(new Color(20, 24, 33));

        // 1. TOP HEADER (KPI & Stats)
        JPanel topBar = new JPanel(new BorderLayout(10, 0));
        topBar.setBackground(new Color(30, 41, 59));
        topBar.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createLineBorder(new Color(71, 85, 105), 1),
                BorderFactory.createEmptyBorder(10, 14, 10, 14)
        ));

        summaryLabel = new JLabel("Goals Tracking: Active");
        summaryLabel.setFont(new Font("Segoe UI", Font.BOLD, 13));
        summaryLabel.setForeground(Color.WHITE);

        topBar.add(summaryLabel, BorderLayout.WEST);
        add(topBar, BorderLayout.NORTH);

        // 2. CENTER: Goal Cards
        goalsContainer = new JPanel();
        goalsContainer.setLayout(new BoxLayout(goalsContainer, BoxLayout.Y_AXIS));
        goalsContainer.setBackground(new Color(20, 24, 33));

        JScrollPane scrollPane = new JScrollPane(goalsContainer);
        scrollPane.setBorder(BorderFactory.createEmptyBorder());
        scrollPane.getVerticalScrollBar().setUnitIncrement(16);
        add(scrollPane, BorderLayout.CENTER);

        // 3. BOTTOM: Goal Creator Form
        add(createGoalInputPanel(), BorderLayout.SOUTH);

        EventBus.getInstance().subscribe("GOALS_UPDATED", this);
        updateView();
    }

    private JPanel createGoalInputPanel() {
        JPanel form = new JPanel(new FlowLayout(FlowLayout.LEFT, 10, 10));
        form.setBackground(new Color(30, 41, 59));
        form.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createLineBorder(new Color(55, 65, 81), 1),
                BorderFactory.createEmptyBorder(6, 10, 6, 10)
        ));

        JTextField goalField = new JTextField(18);
        JComboBox<String> categoryCombo = new JComboBox<>(new String[]{"Academic", "Professional", "Personal", "Health"});
        JTextField deadlineField = new JTextField("End of Semester", 12);

        JButton addGoalBtn = new JButton("+ Create Goal");
        addGoalBtn.setFont(new Font("Segoe UI", Font.BOLD, 12));
        addGoalBtn.setBackground(new Color(168, 85, 247));
        addGoalBtn.setForeground(Color.WHITE);
        addGoalBtn.setFocusPainted(false);
        addGoalBtn.setCursor(new Cursor(Cursor.HAND_CURSOR));

        form.add(new JLabel("Goal:"));
        form.add(goalField);
        form.add(new JLabel("Category:"));
        form.add(categoryCombo);
        form.add(new JLabel("Target Deadline:"));
        form.add(deadlineField);
        form.add(addGoalBtn);

        addGoalBtn.addActionListener(e -> {
            String title = goalField.getText().trim();
            if (!title.isEmpty()) {
                String cat = (String) categoryCombo.getSelectedItem();
                String dl = deadlineField.getText().trim();
                service.addGoal(title, cat, dl.isEmpty() ? "This Month" : dl);
                goalField.setText("");
            }
        });

        return form;
    }

    private void updateView() {
        goalsContainer.removeAll();

        List<Goal> goals = service.getGoals();
        int total = goals.size();
        long completed = goals.stream().filter(g -> g.getProgress() >= 1.0).count();
        summaryLabel.setText(String.format("🎯 Strategic Milestones: %d Goals Tracked  •  %d Completed  •  %d Active", 
                total, completed, total - completed));

        for (Goal g : goals) {
            goalsContainer.add(createGoalCard(g));
            goalsContainer.add(Box.createVerticalStrut(12));
        }

        goalsContainer.revalidate();
        goalsContainer.repaint();
    }

    private JPanel createGoalCard(Goal goal) {
        JPanel card = new JPanel(new BorderLayout(10, 10));
        card.setBackground(new Color(30, 41, 59));
        card.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createLineBorder(new Color(55, 65, 81), 1),
                BorderFactory.createEmptyBorder(12, 14, 12, 14)
        ));

        // Top info + Progress Bar
        JPanel top = new JPanel(new BorderLayout(10, 6));
        top.setOpaque(false);

        JLabel titleLabel = new JLabel(goal.getTitle());
        titleLabel.setFont(new Font("Segoe UI", Font.BOLD, 15));
        titleLabel.setForeground(Color.WHITE);

        JLabel meta = new JLabel(String.format("[%s] • Deadline: %s • %d%% Completed", 
                goal.getCategory(), goal.getDeadline(), goal.getProgressPercentage()));
        meta.setFont(new Font("Segoe UI", Font.BOLD, 11));
        meta.setForeground(new Color(147, 197, 253));

        JProgressBar pBar = new JProgressBar(0, 100);
        pBar.setValue(goal.getProgressPercentage());
        pBar.setStringPainted(true);
        pBar.setFont(new Font("Segoe UI", Font.BOLD, 11));
        pBar.setPreferredSize(new Dimension(150, 16));
        if (goal.getProgress() >= 1.0) {
            pBar.setForeground(new Color(34, 197, 94));
        } else {
            pBar.setForeground(new Color(59, 130, 246));
        }

        JPanel titleAndMeta = new JPanel();
        titleAndMeta.setLayout(new BoxLayout(titleAndMeta, BoxLayout.Y_AXIS));
        titleAndMeta.setOpaque(false);
        titleAndMeta.add(titleLabel);
        titleAndMeta.add(Box.createVerticalStrut(3));
        titleAndMeta.add(meta);

        top.add(titleAndMeta, BorderLayout.WEST);
        top.add(pBar, BorderLayout.EAST);
        card.add(top, BorderLayout.NORTH);

        // Center Milestones List
        JPanel milestonesPanel = new JPanel();
        milestonesPanel.setLayout(new BoxLayout(milestonesPanel, BoxLayout.Y_AXIS));
        milestonesPanel.setOpaque(false);
        milestonesPanel.setBorder(BorderFactory.createEmptyBorder(6, 4, 6, 4));

        List<Milestone> milestones = goal.getMilestones();
        for (int i = 0; i < milestones.size(); i++) {
            final int index = i;
            Milestone m = milestones.get(i);

            JPanel mRow = new JPanel(new FlowLayout(FlowLayout.LEFT, 8, 2));
            mRow.setOpaque(false);

            JCheckBox cb = new JCheckBox(m.getDescription());
            cb.setSelected(m.isCompleted());
            cb.setFont(new Font("Segoe UI", m.isCompleted() ? Font.ITALIC : Font.PLAIN, 12));
            cb.setForeground(m.isCompleted() ? new Color(156, 163, 175) : new Color(229, 231, 235));
            cb.setOpaque(false);
            cb.addActionListener(e -> service.completeMilestone(goal.getId(), index));

            mRow.add(cb);
            milestonesPanel.add(mRow);
        }
        card.add(milestonesPanel, BorderLayout.CENTER);

        // Bottom: Add Milestone Input
        JPanel addMsPanel = new JPanel(new FlowLayout(FlowLayout.LEFT, 6, 2));
        addMsPanel.setOpaque(false);

        JTextField msInput = new JTextField(20);
        JButton addMsBtn = new JButton("+ Milestone");
        addMsBtn.setFont(new Font("Segoe UI", Font.PLAIN, 11));
        addMsBtn.setBackground(new Color(59, 130, 246));
        addMsBtn.setForeground(Color.WHITE);
        addMsBtn.setFocusPainted(false);

        JButton delGoalBtn = new JButton("Delete Goal");
        delGoalBtn.setFont(new Font("Segoe UI", Font.PLAIN, 11));
        delGoalBtn.setBackground(new Color(239, 68, 68));
        delGoalBtn.setForeground(Color.WHITE);
        delGoalBtn.setFocusPainted(false);

        addMsBtn.addActionListener(e -> {
            String desc = msInput.getText().trim();
            if (!desc.isEmpty()) {
                service.addMilestoneToGoal(goal.getId(), desc);
                msInput.setText("");
            }
        });

        delGoalBtn.addActionListener(e -> service.deleteGoal(goal.getId()));

        addMsPanel.add(new JLabel("Add Step:"));
        addMsPanel.add(msInput);
        addMsPanel.add(addMsBtn);
        addMsPanel.add(delGoalBtn);

        card.add(addMsPanel, BorderLayout.SOUTH);
        return card;
    }

    @Override
    public void onEvent(NexusEvent event) {
        if ("GOALS_UPDATED".equals(event.getType())) {
            SwingUtilities.invokeLater(() -> updateView());
        }
    }
}
