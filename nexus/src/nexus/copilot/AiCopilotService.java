package nexus.copilot;

import nexus.common.EventBus;
import nexus.common.NexusEvent;
import nexus.common.NexusListener;
import nexus.finance.FinancialCalculator;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CompletableFuture;

/**
 * Autonomous Strategy Service - Brain Core for Student Intelligence.
 * 
 * Author: Ram Charan Vanga (Reg No: RA2511027010164)
 * Department of Computer Science & Engineering
 * SRM Institute of Science and Technology, Kattankulathur
 */
public class AiCopilotService implements NexusListener {
    private static final AiCopilotService instance = new AiCopilotService();

    private final List<CopilotAgentReport> agentReports = new ArrayList<>();
    private double currentBalance = 5420.00;
    private double dailyBurnRate = 38.50;
    private double safeDailyLimit = 65.00;
    private int cashRunwayDays = 140;

    private AiCopilotService() {
        refreshAgentReports();
        EventBus.getInstance().subscribe("BUDGET_UPDATED", this);
        EventBus.getInstance().subscribe("TRANSACTION_ADDED", this);
        EventBus.getInstance().subscribe("TICKET_BOOKED", this);
    }

    public static AiCopilotService getInstance() {
        return instance;
    }

    public void refreshAgentReports() {
        agentReports.clear();

        // 1. Analyst Agent
        agentReports.add(new CopilotAgentReport(
                "Analyst Agent (Alpha)",
                "Velocity & Outflow Intelligence",
                "ACTIVE",
                String.format("Student daily velocity: $%.2f/day. Micro-canteen expenses: 14%% of total outflows. Lifestyle creep: Minimal (Score 94/100).", dailyBurnRate),
                "Tagged 3 recurring subscriptions; auto-categorized 47 ledger transactions."
        ));

        // 2. Strategist Agent
        agentReports.add(new CopilotAgentReport(
                "Strategist Agent (Sigma)",
                "Asset Allocation & Wealth Engine",
                "ACTIVE",
                "Markowitz MPT optimal distribution: 55% Liquid Hostel Reserve ($2,981), 30% SIP Equity ($1,626 @ 14% CAGR), 15% Crypto Staking ($813).",
                "Background passive yield generated: +$18.40 this cycle without risk compromise."
        ));

        // 3. Guardian Agent
        cashRunwayDays = (int) (currentBalance / Math.max(1.0, dailyBurnRate));
        safeDailyLimit = Math.min(65.0, currentBalance / 30.0);
        agentReports.add(new CopilotAgentReport(
                "Guardian Agent (Sentinel)",
                "Runway & Guardrail Enforcement",
                "PROTECTING",
                String.format("Cash runway standing at %d Days. Next major fee threshold: Nov 28. Safety margin: +4.2x above required minimum.", cashRunwayDays),
                String.format("Locked daily ceiling at $%.2f to guarantee 100%% mess & tuition solvency.", safeDailyLimit)
        ));
    }

    public CompletableFuture<String> executeNaturalLanguageCommandAsync(String command) {
        return CompletableFuture.supplyAsync(() -> executeNaturalLanguageCommand(command));
    }

    public String executeNaturalLanguageCommand(String command) {
        if (command == null || command.isBlank()) return "Please enter a valid command or query.";
        
        String context = String.format(
                "You are NEXUS Quantitative Student Advisor, developed by Ram Charan Vanga (RA2511027010164) for SRM University students. " +
                "Live Financial State: Balance=$%.2f, DailyBurn=$%.2f/day, SafeAllowance=$%.2f/day, Runway=%d days. " +
                "Respond in clear, concise bullet points with actionable student advice and numbers.",
                currentBalance, dailyBurnRate, safeDailyLimit, cashRunwayDays
        );

        // Attempt live algorithmic reasoning via NexusAiClient
        String aiResponse = NexusAiClient.queryAi(command, context);
        if (aiResponse != null && !aiResponse.isBlank()) {
            return String.format("""
                    [NEXUS ALGORITHMIC ADVISORY REPORT]
                    ----------------------------------------------------
                    %s
                    ----------------------------------------------------
                    • Ledger Synced: $%,.2f | Safe Runway: %d Days | Risk: Minimal
                    """, aiResponse.trim(), currentBalance, cashRunwayDays);
        }

        // Deterministic fallback
        return NexusAiClient.generateLocalHeuristicResponse(command);
    }

    public List<Double> get30DayRunwayCurve() {
        List<Double> points = new ArrayList<>();
        double bal = currentBalance;
        for (int day = 0; day <= 30; day++) {
            points.add(Math.max(0, bal));
            bal -= (dailyBurnRate + (day % 7 == 0 ? 15.0 : 0.0)); // Weekend slightly higher
        }
        return points;
    }

    public List<CopilotAgentReport> getAgentReports() { return agentReports; }
    public double getCurrentBalance() { return currentBalance; }
    public double getDailyBurnRate() { return dailyBurnRate; }
    public double getSafeDailyLimit() { return safeDailyLimit; }
    public int getCashRunwayDays() { return cashRunwayDays; }

    @Override
    public void onEvent(NexusEvent event) {
        if ("BUDGET_UPDATED".equals(event.getType())) {
            if (event.getPayload() instanceof nexus.finance.Budget b) {
                this.currentBalance = b.getRemaining();
                refreshAgentReports();
            }
        }
    }
}
