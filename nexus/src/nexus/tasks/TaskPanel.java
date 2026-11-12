package nexus.tasks;

import javax.swing.*;
import java.awt.*;
import java.util.List;
import nexus.common.EventBus;
import nexus.common.NexusEvent;
import nexus.common.NexusListener;

public class TaskPanel extends JPanel implements NexusListener {
    private final TaskService service;
    private JPanel taskListContainer;
    private JLabel taskSummaryLabel;
    private JComboBox<String> filterCombo;

    public TaskPanel(TaskService service) {
        this.service = service;
        setLayout(new BorderLayout(15, 15));
        setBorder(BorderFactory.createEmptyBorder(15, 15, 15, 15));
        setBackground(new Color(20, 24, 33));

        // 1. TOP HEADER (KPI & Filters)
        JPanel topBar = new JPanel(new BorderLayout(10, 0));
        topBar.setBackground(new Color(30, 41, 59));
        topBar.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createLineBorder(new Color(71, 85, 105), 1),
                BorderFactory.createEmptyBorder(10, 14, 10, 14)
        ));

        taskSummaryLabel = new JLabel("Tasks Overview: Loading...");
        taskSummaryLabel.setFont(new Font("Segoe UI", Font.BOLD, 13));
        taskSummaryLabel.setForeground(Color.WHITE);

        JPanel filterPanel = new JPanel(new FlowLayout(FlowLayout.RIGHT, 6, 0));
        filterPanel.setOpaque(false);
        filterPanel.add(new JLabel("Filter:"));
        filterCombo = new JComboBox<>(new String[]{"All Tasks", "Pending Only", "Completed Only", "High Priority"});
        filterCombo.addActionListener(e -> renderTasks(service.getTasks()));
        filterPanel.add(filterCombo);

        topBar.add(taskSummaryLabel, BorderLayout.WEST);
        topBar.add(filterPanel, BorderLayout.EAST);
        add(topBar, BorderLayout.NORTH);

        // 2. CENTER: Task Card List
        taskListContainer = new JPanel();
        taskListContainer.setLayout(new BoxLayout(taskListContainer, BoxLayout.Y_AXIS));
        taskListContainer.setBackground(new Color(20, 24, 33));

        JScrollPane scrollPane = new JScrollPane(taskListContainer);
        scrollPane.setBorder(BorderFactory.createEmptyBorder());
        scrollPane.getVerticalScrollBar().setUnitIncrement(16);
        add(scrollPane, BorderLayout.CENTER);

        // 3. BOTTOM: Task Creator Form
        add(createTaskInputPanel(), BorderLayout.SOUTH);

        EventBus.getInstance().subscribe("TASKS_UPDATED", this);
        renderTasks(service.getTasks());
    }

    private JPanel createTaskInputPanel() {
        JPanel form = new JPanel(new FlowLayout(FlowLayout.LEFT, 10, 10));
        form.setBackground(new Color(30, 41, 59));
        form.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createLineBorder(new Color(55, 65, 81), 1),
                BorderFactory.createEmptyBorder(6, 10, 6, 10)
        ));

        JTextField titleField = new JTextField(18);
        JComboBox<TaskPriority> priorityCombo = new JComboBox<>(TaskPriority.values());
        priorityCombo.setSelectedItem(TaskPriority.MEDIUM);

        JComboBox<String> categoryCombo = new JComboBox<>(new String[]{"Academic", "Project", "Coding", "Personal", "Other"});
        JTextField dueDateField = new JTextField("Tomorrow", 8);

        JButton addBtn = new JButton("+ Add Task");
        addBtn.setFont(new Font("Segoe UI", Font.BOLD, 12));
        addBtn.setBackground(new Color(16, 185, 129));
        addBtn.setForeground(Color.WHITE);
        addBtn.setFocusPainted(false);
        addBtn.setCursor(new Cursor(Cursor.HAND_CURSOR));

        form.add(new JLabel("Title:"));
        form.add(titleField);
        form.add(new JLabel("Priority:"));
        form.add(priorityCombo);
        form.add(new JLabel("Category:"));
        form.add(categoryCombo);
        form.add(new JLabel("Due:"));
        form.add(dueDateField);
        form.add(addBtn);

        addBtn.addActionListener(e -> {
            String title = titleField.getText().trim();
            if (!title.isEmpty()) {
                TaskPriority prio = (TaskPriority) priorityCombo.getSelectedItem();
                String cat = (String) categoryCombo.getSelectedItem();
                String due = dueDateField.getText().trim();
                service.addTask(title, prio, cat, due.isEmpty() ? "Today" : due);
                titleField.setText("");
            }
        });

        return form;
    }

    private void renderTasks(List<Task> tasks) {
        taskListContainer.removeAll();

        int total = tasks.size();
        long completed = tasks.stream().filter(Task::isCompleted).count();
        long pending = total - completed;
        taskSummaryLabel.setText(String.format("Tasks: %d Total  •  %d Pending  •  %d Completed (%.0f%% Done)", 
                total, pending, completed, total > 0 ? (completed * 100.0 / total) : 0));

        String filter = (String) filterCombo.getSelectedItem();

        boolean hasItems = false;
        for (Task t : tasks) {
            if ("Pending Only".equals(filter) && t.isCompleted()) continue;
            if ("Completed Only".equals(filter) && !t.isCompleted()) continue;
            if ("High Priority".equals(filter) && t.getPriority() != TaskPriority.HIGH && t.getPriority() != TaskPriority.URGENT) continue;

            taskListContainer.add(createTaskCard(t));
            taskListContainer.add(Box.createVerticalStrut(8));
            hasItems = true;
        }

        if (!hasItems) {
            JLabel empty = new JLabel("No tasks matching current filter.");
            empty.setFont(new Font("Segoe UI", Font.ITALIC, 13));
            empty.setForeground(new Color(156, 163, 175));
            empty.setBorder(BorderFactory.createEmptyBorder(30, 30, 30, 30));
            taskListContainer.add(empty);
        }

        taskListContainer.revalidate();
        taskListContainer.repaint();
    }

    private JPanel createTaskCard(Task task) {
        JPanel card = new JPanel(new BorderLayout(12, 0));
        card.setBackground(new Color(30, 41, 59));

        Color priorityColor = switch (task.getPriority()) {
            case URGENT -> new Color(220, 38, 38);
            case HIGH -> new Color(239, 68, 68);
            case MEDIUM -> new Color(245, 158, 11);
            case LOW -> new Color(16, 185, 129);
            default -> new Color(156, 163, 175);
        };

        card.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createMatteBorder(0, 4, 0, 0, priorityColor),
                BorderFactory.createEmptyBorder(8, 12, 8, 12)
        ));
        card.setMaximumSize(new Dimension(2000, 60));

        // Left Checkbox
        JCheckBox doneBox = new JCheckBox();
        doneBox.setSelected(task.isCompleted());
        doneBox.setOpaque(false);
        doneBox.addActionListener(e -> {
            if (doneBox.isSelected()) {
                service.completeTask(task.getId());
            } else {
                task.setCompleted(false);
                service.setTasks(service.getTasks());
            }
        });
        card.add(doneBox, BorderLayout.WEST);

        // Center: Title + Badges
        JPanel center = new JPanel();
        center.setLayout(new BoxLayout(center, BoxLayout.Y_AXIS));
        center.setOpaque(false);

        JLabel titleLabel = new JLabel(task.getTitle());
        titleLabel.setFont(new Font("Segoe UI", task.isCompleted() ? Font.ITALIC : Font.BOLD, 13));
        if (task.isCompleted()) {
            titleLabel.setForeground(new Color(156, 163, 175));
        } else {
            titleLabel.setForeground(Color.WHITE);
        }

        JLabel badgeLabel = new JLabel(String.format("Priority: %s  •  Category: %s  •  Due: %s", 
                task.getPriority(), task.getCategory(), task.getDueDate()));
        badgeLabel.setFont(new Font("Segoe UI", Font.PLAIN, 11));
        badgeLabel.setForeground(new Color(147, 197, 253));

        center.add(titleLabel);
        center.add(Box.createVerticalStrut(2));
        center.add(badgeLabel);
        card.add(center, BorderLayout.CENTER);

        // Right Delete
        JButton delBtn = new JButton("🗑️");
        delBtn.setOpaque(false);
        delBtn.setContentAreaFilled(false);
        delBtn.setBorderPainted(false);
        delBtn.setCursor(new Cursor(Cursor.HAND_CURSOR));
        delBtn.addActionListener(e -> service.deleteTask(task.getId()));
        card.add(delBtn, BorderLayout.EAST);

        return card;
    }

    @Override
    public void onEvent(NexusEvent event) {
        if ("TASKS_UPDATED".equals(event.getType())) {
            SwingUtilities.invokeLater(() -> {
                @SuppressWarnings("unchecked")
                List<Task> updated = (List<Task>) event.getPayload();
                renderTasks(updated);
            });
        }
    }
}
