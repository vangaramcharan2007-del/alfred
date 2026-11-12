package nexus.tasks;

import nexus.common.EventBus;
import nexus.common.NexusEvent;
import nexus.common.NexusListener;
import java.util.ArrayList;
import java.util.List;

public class TaskService implements NexusListener {
    private List<Task> tasks;
    
    public TaskService() {
        tasks = new ArrayList<>();
        // Seed initial tasks
        addTask("Prepare Review 2 Slides & Live Demo", TaskPriority.HIGH, "Academic", "Tomorrow");
        addTask("Verify Real-Time API Connections", TaskPriority.HIGH, "Project", "Today");
        addTask("Setup Environment & Classpath", TaskPriority.MEDIUM, "Coding", "Completed");

        EventBus.getInstance().subscribe("ITEM_PURCHASED", this);
        EventBus.getInstance().subscribe("MEDIA_ADDED", this);
        EventBus.getInstance().subscribe("MEDIA_COMPLETED", this);
    }
    
    public void addTask(String title, TaskPriority priority) {
        addTask(title, priority, "General", "Today");
    }

    public void addTask(String title, TaskPriority priority, String category, String dueDate) {
        Task t = new Task(title, priority, category, dueDate);
        tasks.add(0, t);
        EventBus.getInstance().publish(new NexusEvent("TASK_ADDED", t, "Tasks"));
        EventBus.getInstance().publish(new NexusEvent("TASKS_UPDATED", tasks, "Tasks"));
    }
    
    public void completeTask(String id) {
        for (Task t : tasks) {
            if (t.getId().equals(id)) {
                t.setCompleted(true);
                EventBus.getInstance().publish(new NexusEvent("TASK_COMPLETED", t, "Tasks"));
                EventBus.getInstance().publish(new NexusEvent("TASKS_UPDATED", tasks, "Tasks"));
                break;
            }
        }
    }

    public void deleteTask(String id) {
        Task removed = null;
        for (int i = 0; i < tasks.size(); i++) {
            if (tasks.get(i).getId().equals(id)) {
                removed = tasks.remove(i);
                break;
            }
        }
        if (removed != null) {
            EventBus.getInstance().publish(new NexusEvent("TASK_DELETED", removed, "Tasks"));
            EventBus.getInstance().publish(new NexusEvent("TASKS_UPDATED", tasks, "Tasks"));
        }
    }
    
    @Override
    public void onEvent(NexusEvent event) {
        if ("ITEM_PURCHASED".equals(event.getType())) {
            nexus.market.Product product = (nexus.market.Product) event.getPayload();
            String pName = product.getName().toLowerCase();
            for (Task t : tasks) {
                if (!t.isCompleted() && t.getTitle().toLowerCase().contains(pName)) {
                    completeTask(t.getId());
                }
            }
        } else if ("MEDIA_ADDED".equals(event.getType())) {
            nexus.media.MediaItem media = (nexus.media.MediaItem) event.getPayload();
            String prefix = media.getType() == nexus.media.MediaType.BOOK ? "Read" : "Watch";
            addTask(prefix + ": " + media.getTitle(), TaskPriority.MEDIUM, "Media", "Upcoming");
        } else if ("MEDIA_COMPLETED".equals(event.getType())) {
            nexus.media.MediaItem media = (nexus.media.MediaItem) event.getPayload();
            String mediaTitle = media.getTitle().toLowerCase();
            for (Task t : tasks) {
                if (!t.isCompleted() && t.getTitle().toLowerCase().contains(mediaTitle)) {
                    completeTask(t.getId());
                    break;
                }
            }
        }
    }
    
    public List<Task> getTasks() { return tasks; }
    
    public void setTasks(List<Task> loadedTasks) {
        if (loadedTasks != null && !loadedTasks.isEmpty()) {
            this.tasks = loadedTasks;
            EventBus.getInstance().publish(new NexusEvent("TASKS_UPDATED", tasks, "Tasks"));
        }
    }
}
