package nexus.goals;

import nexus.common.IdGenerator;
import java.util.ArrayList;
import java.util.List;

public class Goal {
    private String id;
    private String title;
    private String category;
    private String deadline;
    private List<Milestone> milestones;
    
    public Goal(String title) {
        this(title, "Academic", "End of Semester");
    }

    public Goal(String title, String category, String deadline) {
        this.id = IdGenerator.generateId();
        this.title = title;
        this.category = category != null ? category : "Academic";
        this.deadline = deadline != null ? deadline : "End of Semester";
        this.milestones = new ArrayList<>();
    }

    public Goal(String id, String title, String category, String deadline, List<Milestone> milestones) {
        this.id = id;
        this.title = title;
        this.category = category != null ? category : "Academic";
        this.deadline = deadline != null ? deadline : "End of Semester";
        this.milestones = milestones != null ? milestones : new ArrayList<>();
    }
    
    public String getId() { return id; }
    public String getTitle() { return title; }
    public String getCategory() { return category; }
    public String getDeadline() { return deadline; }
    public List<Milestone> getMilestones() { return milestones; }
    
    public void addMilestone(Milestone m) {
        milestones.add(m);
    }
    
    public double getProgress() {
        if (milestones.isEmpty()) return 0.0;
        long completedCount = milestones.stream().filter(Milestone::isCompleted).count();
        return (double) completedCount / milestones.size();
    }

    public int getProgressPercentage() {
        return (int) (getProgress() * 100);
    }
}
