package nexus.goals;

import nexus.common.IdGenerator;

public class Milestone {
    private String id;
    private String description;
    private boolean completed;
    
    public Milestone(String description) {
        this(IdGenerator.generateId(), description, false);
    }

    public Milestone(String id, String description, boolean completed) {
        this.id = id != null ? id : IdGenerator.generateId();
        this.description = description;
        this.completed = completed;
    }
    
    public String getId() { return id; }
    public String getDescription() { return description; }
    public boolean isCompleted() { return completed; }
    public void setCompleted(boolean completed) { this.completed = completed; }
}
