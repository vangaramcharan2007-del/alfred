package nexus.goals;

import nexus.common.EventBus;
import nexus.common.NexusEvent;
import nexus.common.NexusListener;
import java.util.ArrayList;
import java.util.List;

public class GoalService implements NexusListener {
    private List<Goal> goals;
    
    public GoalService() {
        goals = new ArrayList<>();
        EventBus.getInstance().subscribe("ITEM_PURCHASED", this);
        EventBus.getInstance().subscribe("TASK_COMPLETED", this);

        seedDefaults();
    }

    private void seedDefaults() {
        Goal g1 = new Goal("A+ Grade in AOOP Review 2", "Academic", "Nov 2, 2026");
        g1.addMilestone(new Milestone("Implement Real-Time TVMaze & CoinGecko APIs"));
        g1.addMilestone(new Milestone("Build Modern UI with FlatLaf Charts"));
        g1.addMilestone(new Milestone("Verify Full SQLite Database Persistence"));
        goals.add(g1);

        Goal g2 = new Goal("Master Full-Stack Java Desktop Architecture", "Professional", "December 2026");
        g2.addMilestone(new Milestone("Study Event-Driven Pub/Sub Design Pattern"));
        g2.addMilestone(new Milestone("Implement Thread-Safe Database Write Queues"));
        goals.add(g2);
    }
    
    public void addGoal(String title) {
        addGoal(title, "Academic", "This Month");
    }

    public void addGoal(String title, String category, String deadline) {
        Goal g = new Goal(title, category, deadline);
        goals.add(0, g);
        EventBus.getInstance().publish(new NexusEvent("GOAL_ADDED", g, "Goals"));
        EventBus.getInstance().publish(new NexusEvent("GOALS_UPDATED", goals, "Goals"));
    }
    
    public void addMilestoneToGoal(String goalId, String milestoneDesc) {
        for (Goal g : goals) {
            if (g.getId().equals(goalId)) {
                Milestone m = new Milestone(milestoneDesc);
                g.addMilestone(m);
                EventBus.getInstance().publish(new NexusEvent("MILESTONE_ADDED", m, "Goals"));
                EventBus.getInstance().publish(new NexusEvent("GOALS_UPDATED", goals, "Goals"));
                break;
            }
        }
    }
    
    public void completeMilestone(String goalId, int milestoneIndex) {
        for (Goal g : goals) {
            if (g.getId().equals(goalId)) {
                if (milestoneIndex >= 0 && milestoneIndex < g.getMilestones().size()) {
                    Milestone m = g.getMilestones().get(milestoneIndex);
                    m.setCompleted(!m.isCompleted()); // Toggle
                    EventBus.getInstance().publish(new NexusEvent("GOALS_UPDATED", goals, "Goals"));
                    
                    if (g.getProgress() >= 1.0) {
                        EventBus.getInstance().publish(new NexusEvent("GOAL_COMPLETED", g, "Goals"));
                    }
                }
                break;
            }
        }
    }

    public void deleteGoal(String id) {
        Goal removed = null;
        for (int i = 0; i < goals.size(); i++) {
            if (goals.get(i).getId().equals(id)) {
                removed = goals.remove(i);
                break;
            }
        }
        if (removed != null) {
            EventBus.getInstance().publish(new NexusEvent("GOAL_DELETED", removed, "Goals"));
            EventBus.getInstance().publish(new NexusEvent("GOALS_UPDATED", goals, "Goals"));
        }
    }
    
    @Override
    public void onEvent(NexusEvent event) {
        if ("ITEM_PURCHASED".equals(event.getType())) {
            nexus.market.Product product = (nexus.market.Product) event.getPayload();
            String pName = product.getName().toLowerCase();
            for (Goal g : goals) {
                for (int i = 0; i < g.getMilestones().size(); i++) {
                    Milestone m = g.getMilestones().get(i);
                    if (!m.isCompleted() && m.getDescription().toLowerCase().contains(pName)) {
                        completeMilestone(g.getId(), i);
                    }
                }
            }
        } else if ("TASK_COMPLETED".equals(event.getType())) {
            nexus.tasks.Task task = (nexus.tasks.Task) event.getPayload();
            String taskTitle = task.getTitle().toLowerCase();
            for (Goal g : goals) {
                for (int i = 0; i < g.getMilestones().size(); i++) {
                    Milestone m = g.getMilestones().get(i);
                    if (!m.isCompleted() && taskTitle.contains(m.getDescription().toLowerCase())) {
                        completeMilestone(g.getId(), i);
                    }
                }
            }
        }
    }
    
    public List<Goal> getGoals() { return goals; }

    public void setGoals(List<Goal> loadedGoals) {
        if (loadedGoals != null && !loadedGoals.isEmpty()) {
            this.goals = loadedGoals;
            EventBus.getInstance().publish(new NexusEvent("GOALS_UPDATED", goals, "Goals"));
        }
    }
}
