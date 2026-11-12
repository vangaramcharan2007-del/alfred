package nexus.tasks;

import java.text.SimpleDateFormat;
import java.util.Date;
import nexus.common.IdGenerator;

public class Task {
    private String id;
    private String title;
    private TaskPriority priority;
    private boolean completed;
    private String dueDate;
    private String category;
    
    public Task(String title, TaskPriority priority) {
        this(title, priority, "General", "Today");
    }

    public Task(String title, TaskPriority priority, String category, String dueDate) {
        this.id = IdGenerator.generateId();
        this.title = title;
        this.priority = priority != null ? priority : TaskPriority.MEDIUM;
        this.completed = false;
        this.category = category != null ? category : "General";
        this.dueDate = dueDate != null ? dueDate : "Today";
    }

    public Task(String id, String title, TaskPriority priority, boolean completed) {
        this(id, title, priority, completed, "General", "Today");
    }

    public Task(String id, String title, TaskPriority priority, boolean completed, String category, String dueDate) {
        this.id = id;
        this.title = title;
        this.priority = priority != null ? priority : TaskPriority.MEDIUM;
        this.completed = completed;
        this.category = category != null ? category : "General";
        this.dueDate = dueDate != null ? dueDate : "Today";
    }
    
    public String getId() { return id; }
    public String getTitle() { return title; }
    public TaskPriority getPriority() { return priority; }
    public boolean isCompleted() { return completed; }
    public String getDueDate() { return dueDate; }
    public String getCategory() { return category; }
    
    public void setCompleted(boolean completed) { this.completed = completed; }
    public void setDueDate(String dueDate) { this.dueDate = dueDate; }
    public void setCategory(String category) { this.category = category; }
}
