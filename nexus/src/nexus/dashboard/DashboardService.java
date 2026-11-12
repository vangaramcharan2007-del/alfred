package nexus.dashboard;

import nexus.common.EventBus;
import nexus.common.NexusEvent;
import nexus.common.NexusListener;
import nexus.finance.Budget;
import java.util.HashMap;
import java.util.Map;

public class DashboardService implements NexusListener {
    private Map<String, Object> summaryData;
    
    public DashboardService() {
        summaryData = new HashMap<>();
        summaryData.put("XP", 100);
        summaryData.put("budget_remaining", 10000.0);
        summaryData.put("tasks_total", 0);
        summaryData.put("tasks_completed", 0);
        summaryData.put("goals_total", 0);
        summaryData.put("goals_completed", 0);
        summaryData.put("media_total", 0);
        
        EventBus.getInstance().subscribe("XP_UPDATED", this);
        EventBus.getInstance().subscribe("BUDGET_UPDATED", this);
        EventBus.getInstance().subscribe("TASKS_UPDATED", this);
        EventBus.getInstance().subscribe("GOALS_UPDATED", this);
        EventBus.getInstance().subscribe("MEDIA_UPDATED", this);
    }
    
    @Override
    public void onEvent(NexusEvent event) {
        if ("XP_UPDATED".equals(event.getType())) {
            summaryData.put("XP", event.getPayload());
            EventBus.getInstance().publish(new NexusEvent("DASHBOARD_UPDATED", summaryData, "Dashboard"));
        } else if ("BUDGET_UPDATED".equals(event.getType())) {
            Budget b = (Budget) event.getPayload();
            summaryData.put("budget_remaining", b.getRemaining());
            EventBus.getInstance().publish(new NexusEvent("DASHBOARD_UPDATED", summaryData, "Dashboard"));
        } else if ("TASKS_UPDATED".equals(event.getType())) {
            @SuppressWarnings("unchecked")
            java.util.List<nexus.tasks.Task> tasks = (java.util.List<nexus.tasks.Task>) event.getPayload();
            long completed = tasks.stream().filter(nexus.tasks.Task::isCompleted).count();
            summaryData.put("tasks_total", tasks.size());
            summaryData.put("tasks_completed", (int) completed);
            EventBus.getInstance().publish(new NexusEvent("DASHBOARD_UPDATED", summaryData, "Dashboard"));
        } else if ("GOALS_UPDATED".equals(event.getType())) {
            @SuppressWarnings("unchecked")
            java.util.List<nexus.goals.Goal> goals = (java.util.List<nexus.goals.Goal>) event.getPayload();
            summaryData.put("goals_total", goals.size());
            long goalsCompleted = goals.stream().filter(g -> g.getProgress() >= 1.0).count();
            summaryData.put("goals_completed", (int) goalsCompleted);
            EventBus.getInstance().publish(new NexusEvent("DASHBOARD_UPDATED", summaryData, "Dashboard"));
        } else if ("MEDIA_UPDATED".equals(event.getType())) {
            @SuppressWarnings("unchecked")
            java.util.List<nexus.media.MediaItem> media = (java.util.List<nexus.media.MediaItem>) event.getPayload();
            summaryData.put("media_total", media.size());
            EventBus.getInstance().publish(new NexusEvent("DASHBOARD_UPDATED", summaryData, "Dashboard"));
        }
    }
    
    public Map<String, Object> getSummaryData() { return summaryData; }
}

