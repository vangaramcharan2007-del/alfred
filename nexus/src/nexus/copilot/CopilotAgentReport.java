package nexus.copilot;

public class CopilotAgentReport {
    private final String agentName;
    private final String role;
    private final String status;
    private final String insight;
    private final String actionTaken;

    public CopilotAgentReport(String agentName, String role, String status, String insight, String actionTaken) {
        this.agentName = agentName;
        this.role = role;
        this.status = status;
        this.insight = insight;
        this.actionTaken = actionTaken;
    }

    public String getAgentName() { return agentName; }
    public String getRole() { return role; }
    public String getStatus() { return status; }
    public String getInsight() { return insight; }
    public String getActionTaken() { return actionTaken; }
}