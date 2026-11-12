package nexus.finance;

import javax.swing.*;
import javax.swing.table.DefaultTableCellRenderer;
import javax.swing.table.DefaultTableModel;
import java.awt.*;
import java.text.SimpleDateFormat;
import java.util.List;
import java.util.Map;
import nexus.analytics.PieChartPanel;
import nexus.common.EventBus;
import nexus.common.NexusEvent;
import nexus.common.NexusListener;

public class FinancePanel extends JPanel implements NexusListener {
    private final FinanceService service;
    private final SimpleDateFormat dateFormat = new SimpleDateFormat("MMM dd, HH:mm");

    // KPI Cards
    private JLabel totalBudgetVal;
    private JLabel totalSpentVal;
    private JLabel remainingVal;
    private JLabel interestYieldVal;
    private JLabel emiBurdenVal;
    private JLabel runwayVal;

    private JProgressBar budgetProgressBar;
    private JLabel tickerLabel;
    private PieChartPanel pieChartPanel;
    private DefaultTableModel tableModel;
    private JTable transactionTable;

    public FinancePanel(FinanceService service) {
        this.service = service;
        setLayout(new BorderLayout(15, 12));
        setBorder(BorderFactory.createEmptyBorder(12, 12, 12, 12));
        setBackground(new Color(15, 23, 42));

        // 1. TOP SECTION (Ticker + Automated Intelligence KPI Grid + Progress Bar)
        JPanel topContainer = new JPanel();
        topContainer.setLayout(new BoxLayout(topContainer, BoxLayout.Y_AXIS));
        topContainer.setOpaque(false);

        topContainer.add(createTickerBar());
        topContainer.add(Box.createVerticalStrut(8));
        topContainer.add(createAutomatedKpiPanel());
        topContainer.add(Box.createVerticalStrut(8));
        topContainer.add(createPredictiveEngineBanner());
        topContainer.add(Box.createVerticalStrut(8));
        topContainer.add(createProgressBarPanel());

        add(topContainer, BorderLayout.NORTH);

        // 2. CENTER SECTION (Left: Transaction Form & Category Pie Chart | Right: Audit Ledger Table)
        JPanel centerGrid = new JPanel(new GridLayout(1, 2, 14, 0));
        centerGrid.setOpaque(false);

        // Left Panel
        JPanel leftPanel = new JPanel(new BorderLayout(8, 8));
        leftPanel.setOpaque(false);
        leftPanel.add(createInputForm(), BorderLayout.NORTH);

        pieChartPanel = new PieChartPanel();
        pieChartPanel.setPreferredSize(new Dimension(300, 240));
        pieChartPanel.setBorder(BorderFactory.createTitledBorder(
                BorderFactory.createLineBorder(new Color(51, 65, 85)), 
                "AUTOMATED EXPENSE DISTRIBUTION", 
                0, 0, new Font("Segoe UI", Font.BOLD, 12), Color.CYAN));
        leftPanel.add(pieChartPanel, BorderLayout.CENTER);

        centerGrid.add(leftPanel);

        // Right Panel (Table)
        JPanel rightPanel = new JPanel(new BorderLayout(5, 5));
        rightPanel.setOpaque(false);
        rightPanel.setBorder(BorderFactory.createTitledBorder(
                BorderFactory.createLineBorder(new Color(51, 65, 85)), 
                "REAL-TIME FINANCIAL AUDIT LEDGER (ACID COMPLIANT)", 
                0, 0, new Font("Segoe UI", Font.BOLD, 12), new Color(147, 197, 253)));

        String[] columns = {"Date", "Description", "Category", "Amount"};
        tableModel = new DefaultTableModel(columns, 0) {
            @Override
            public boolean isCellEditable(int row, int col) {
                return false;
            }
        };

        transactionTable = new JTable(tableModel);
        transactionTable.setRowHeight(28);
        transactionTable.setFont(new Font("Segoe UI", Font.PLAIN, 12));
        transactionTable.getTableHeader().setFont(new Font("Segoe UI", Font.BOLD, 12));
        transactionTable.setDefaultRenderer(Object.class, new TransactionCellRenderer());

        JScrollPane tableScroll = new JScrollPane(transactionTable);
        tableScroll.setBorder(BorderFactory.createEmptyBorder());
        rightPanel.add(tableScroll, BorderLayout.CENTER);

        centerGrid.add(rightPanel);
        add(centerGrid, BorderLayout.CENTER);

        // Subscriptions
        EventBus.getInstance().subscribe("TRANSACTION_ADDED", this);
        EventBus.getInstance().subscribe("BUDGET_UPDATED", this);
        EventBus.getInstance().subscribe("TRANSACTIONS_UPDATED", this);
        EventBus.getInstance().subscribe("CRYPTO_RATES_UPDATED", this);

        updateView();
        updateTicker(service.getCryptoPrices());
    }

    private JPanel createTickerBar() {
        JPanel bar = new JPanel(new BorderLayout(10, 0));
        bar.setBackground(new Color(30, 41, 59));
        bar.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createLineBorder(new Color(71, 85, 105), 1),
                BorderFactory.createEmptyBorder(6, 12, 6, 12)
        ));

        JLabel title = new JLabel("● LIVE COINGECKO CRYPTO & FOREX FEED:");
        title.setFont(new Font("Segoe UI", Font.BOLD, 11));
        title.setForeground(new Color(52, 211, 153));

        tickerLabel = new JLabel("Connecting to decentralized price feed...");
        tickerLabel.setFont(new Font("Consolas", Font.PLAIN, 12));
        tickerLabel.setForeground(Color.WHITE);

        JButton refreshBtn = new JButton("🔄 Sync Rates");
        refreshBtn.setFont(new Font("Segoe UI", Font.BOLD, 11));
        refreshBtn.setBackground(new Color(59, 130, 246));
        refreshBtn.setForeground(Color.WHITE);
        refreshBtn.setFocusPainted(false);
        refreshBtn.setCursor(new Cursor(Cursor.HAND_CURSOR));
        refreshBtn.addActionListener(e -> {
            tickerLabel.setText("Fetching live rates from CoinGecko...");
            service.refreshCryptoRates();
        });

        JPanel rightActions = new JPanel(new FlowLayout(FlowLayout.RIGHT, 6, 0));
        rightActions.setOpaque(false);

        JButton copilotBtn = new JButton("📈 Quantitative Engine (P10)");
        copilotBtn.setFont(new Font("Segoe UI", Font.BOLD, 11));
        copilotBtn.setBackground(new Color(16, 185, 129));
        copilotBtn.setForeground(Color.WHITE);
        copilotBtn.setFocusPainted(false);
        copilotBtn.setCursor(new Cursor(Cursor.HAND_CURSOR));
        copilotBtn.addActionListener(e -> EventBus.getInstance().publish(new NexusEvent("NAVIGATION_REQUEST", "Quantitative", "Finance")));

        rightActions.add(copilotBtn);
        rightActions.add(refreshBtn);

        bar.add(title, BorderLayout.WEST);
        bar.add(tickerLabel, BorderLayout.CENTER);
        bar.add(rightActions, BorderLayout.EAST);
        return bar;
    }

    private JPanel createAutomatedKpiPanel() {
        // 6 Automated Financial Intelligence Cards
        JPanel panel = new JPanel(new GridLayout(1, 6, 8, 0));
        panel.setOpaque(false);

        totalBudgetVal = new JLabel("$0.00");
        totalSpentVal = new JLabel("$0.00");
        remainingVal = new JLabel("$0.00");
        interestYieldVal = new JLabel("+$0.00");
        emiBurdenVal = new JLabel("-$0.00");
        runwayVal = new JLabel("0 Days");

        panel.add(createCard("TOTAL CAPITAL", totalBudgetVal, new Color(59, 130, 246)));
        panel.add(createCard("TOTAL EXPENSE", totalSpentVal, new Color(239, 68, 68)));
        panel.add(createCard("NET LIQUID", remainingVal, new Color(16, 185, 129)));
        panel.add(createCard("PASSIVE INTEREST", interestYieldVal, new Color(34, 197, 94)));
        panel.add(createCard("MONTHLY DEBT/EMI", emiBurdenVal, new Color(245, 158, 11)));
        panel.add(createCard("CASH RUNWAY", runwayVal, new Color(168, 85, 247)));

        return panel;
    }

    private JPanel createPredictiveEngineBanner() {
        JPanel bar = new JPanel(new BorderLayout(10, 0));
        bar.setBackground(new Color(24, 30, 42));
        bar.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createLineBorder(new Color(51, 65, 85)),
                BorderFactory.createEmptyBorder(6, 14, 6, 14)
        ));

        JLabel title = new JLabel("💡 Predictive Financial Engine:");
        title.setFont(new Font("Segoe UI", Font.BOLD, 12));
        title.setForeground(new Color(52, 211, 153));

        JLabel text = new JLabel("Daily Burn Rate: $38.50/day • Safe Runway: 140 Days (~4.6 Months) • +$18.40 Passive Compound Yield Earned");
        text.setFont(new Font("Segoe UI", Font.PLAIN, 11));
        text.setForeground(new Color(203, 213, 225));

        JButton askBtn = new JButton("Open Campus Strategy Advisor ⚡");
        askBtn.setFont(new Font("Segoe UI", Font.BOLD, 10));
        askBtn.setBackground(new Color(16, 185, 129));
        askBtn.setForeground(Color.WHITE);
        askBtn.setFocusPainted(false);
        askBtn.setCursor(new Cursor(Cursor.HAND_CURSOR));
        askBtn.addActionListener(e -> EventBus.getInstance().publish(new NexusEvent("OPEN_AI_ASSISTANT", null, "Finance")));

        bar.add(title, BorderLayout.WEST);
        bar.add(text, BorderLayout.CENTER);
        bar.add(askBtn, BorderLayout.EAST);
        return bar;
    }

    private JPanel createCard(String title, JLabel valueLabel, Color accent) {
        JPanel card = new JPanel(new BorderLayout(3, 3));
        card.setBackground(new Color(30, 41, 59));
        card.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createMatteBorder(0, 4, 0, 0, accent),
                BorderFactory.createEmptyBorder(6, 10, 6, 10)
        ));

        JLabel titleLabel = new JLabel(title);
        titleLabel.setFont(new Font("Segoe UI", Font.BOLD, 10));
        titleLabel.setForeground(new Color(156, 163, 175));

        valueLabel.setFont(new Font("Segoe UI", Font.BOLD, 16));
        valueLabel.setForeground(Color.WHITE);

        card.add(titleLabel, BorderLayout.NORTH);
        card.add(valueLabel, BorderLayout.CENTER);
        return card;
    }

    private JPanel createProgressBarPanel() {
        JPanel panel = new JPanel(new BorderLayout(8, 4));
        panel.setOpaque(false);

        JLabel label = new JLabel("Budget Utilization & Burn Velocity:");
        label.setFont(new Font("Segoe UI", Font.BOLD, 11));
        label.setForeground(new Color(209, 213, 219));

        budgetProgressBar = new JProgressBar(0, 100);
        budgetProgressBar.setValue(0);
        budgetProgressBar.setStringPainted(true);
        budgetProgressBar.setFont(new Font("Segoe UI", Font.BOLD, 11));
        budgetProgressBar.setPreferredSize(new Dimension(200, 18));

        JPanel rightControls = new JPanel(new FlowLayout(FlowLayout.RIGHT, 6, 0));
        rightControls.setOpaque(false);

        JButton resetBudgetBtn = new JButton("🔄 Reset Budget");
        resetBudgetBtn.setFont(new Font("Segoe UI", Font.BOLD, 11));
        resetBudgetBtn.setBackground(new Color(59, 130, 246));
        resetBudgetBtn.setForeground(Color.WHITE);
        resetBudgetBtn.setFocusPainted(false);
        resetBudgetBtn.setCursor(new Cursor(Cursor.HAND_CURSOR));
        resetBudgetBtn.addActionListener(e -> showResetBudgetDialog());

        rightControls.add(resetBudgetBtn);

        panel.add(label, BorderLayout.WEST);
        panel.add(budgetProgressBar, BorderLayout.CENTER);
        panel.add(rightControls, BorderLayout.EAST);
        return panel;
    }

    private void showResetBudgetDialog() {
        JDialog dlg = new JDialog((Frame) SwingUtilities.getWindowAncestor(this), "Budget Re-Allocation & Reset", true);
        dlg.setSize(440, 250);
        dlg.setLocationRelativeTo(this);

        JPanel p = new JPanel(new BorderLayout(10, 10));
        p.setBackground(new Color(15, 23, 42));
        p.setBorder(BorderFactory.createEmptyBorder(14, 16, 14, 16));

        JLabel title = new JLabel("⚙️ STUDENT BUDGET RE-ALLOCATION");
        title.setFont(new Font("Segoe UI", Font.BOLD, 14));
        title.setForeground(new Color(56, 189, 248));
        p.add(title, BorderLayout.NORTH);

        JPanel form = new JPanel(new GridLayout(3, 1, 0, 8));
        form.setOpaque(false);

        JLabel info = new JLabel("<html><body style='width:380px; color:#cbd5e1; font-size:11px;'>"
                + "Reset your monthly capital allocation. This recalculates daily burn rate, safe allowance, and runway across all modules.</body></html>");
        form.add(info);

        JPanel inputRow = new JPanel(new BorderLayout(8, 0));
        inputRow.setOpaque(false);
        JLabel amtLabel = new JLabel("New Budget Capital ($):");
        amtLabel.setFont(new Font("Segoe UI", Font.BOLD, 12));
        amtLabel.setForeground(Color.WHITE);
        JTextField budgetInput = new JTextField(String.format("%.2f", service.getBudget().getTotalBudget()));
        budgetInput.setFont(new Font("Consolas", Font.BOLD, 13));
        budgetInput.setBackground(new Color(30, 41, 59));
        budgetInput.setForeground(Color.WHITE);
        budgetInput.setCaretColor(Color.CYAN);
        inputRow.add(amtLabel, BorderLayout.WEST);
        inputRow.add(budgetInput, BorderLayout.CENTER);
        form.add(inputRow);

        JCheckBox clearSpentBox = new JCheckBox("Clear current expenditure & reset spent to $0.00", true);
        clearSpentBox.setFont(new Font("Segoe UI", Font.PLAIN, 11));
        clearSpentBox.setOpaque(false);
        clearSpentBox.setForeground(new Color(203, 213, 225));
        form.add(clearSpentBox);

        p.add(form, BorderLayout.CENTER);

        JPanel btm = new JPanel(new FlowLayout(FlowLayout.RIGHT, 8, 0));
        btm.setOpaque(false);

        JButton cancelBtn = new JButton("Cancel");
        cancelBtn.setBackground(new Color(71, 85, 105));
        cancelBtn.setForeground(Color.WHITE);
        cancelBtn.addActionListener(e -> dlg.dispose());

        JButton applyBtn = new JButton("Apply Budget Reset 🔄");
        applyBtn.setFont(new Font("Segoe UI", Font.BOLD, 11));
        applyBtn.setBackground(new Color(16, 185, 129));
        applyBtn.setForeground(Color.WHITE);
        applyBtn.setCursor(new Cursor(Cursor.HAND_CURSOR));
        applyBtn.addActionListener(e -> {
            try {
                double newAmt = Double.parseDouble(budgetInput.getText().trim());
                if (newAmt <= 0) {
                    JOptionPane.showMessageDialog(dlg, "Please enter a positive budget amount.", "Invalid Budget", JOptionPane.WARNING_MESSAGE);
                    return;
                }
                boolean clearSpent = clearSpentBox.isSelected();
                if (clearSpent) {
                    service.resetBudget(newAmt);
                } else {
                    service.setBudgetCap(newAmt);
                }
                dlg.dispose();
                JOptionPane.showMessageDialog(this, String.format("Student budget successfully re-allocated to $%,.2f!", newAmt), "Budget Re-Allocated", JOptionPane.INFORMATION_MESSAGE);
            } catch (NumberFormatException ex) {
                JOptionPane.showMessageDialog(dlg, "Invalid number format.", "Error", JOptionPane.ERROR_MESSAGE);
            }
        });

        btm.add(cancelBtn);
        btm.add(applyBtn);
        p.add(btm, BorderLayout.SOUTH);

        dlg.setContentPane(p);
        dlg.setVisible(true);
    }

    private JPanel createInputForm() {
        JPanel panel = new JPanel(new GridBagLayout());
        panel.setBackground(new Color(30, 41, 59));
        panel.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createLineBorder(new Color(51, 65, 85)),
                BorderFactory.createEmptyBorder(10, 12, 10, 12)
        ));

        GridBagConstraints gbc = new GridBagConstraints();
        gbc.insets = new Insets(3, 4, 3, 4);
        gbc.fill = GridBagConstraints.HORIZONTAL;

        JTextField descField = new JTextField(12);
        JTextField amountField = new JTextField(8);
        JComboBox<TransactionCategory> catCombo = new JComboBox<>(TransactionCategory.values());
        JComboBox<String> typeCombo = new JComboBox<>(new String[]{"Expense (-)", "Income (+)"});
        JButton addBtn = new JButton("+ Record Entry");
        addBtn.setBackground(new Color(16, 185, 129));
        addBtn.setForeground(Color.WHITE);
        addBtn.setFont(new Font("Segoe UI", Font.BOLD, 11));
        addBtn.setFocusPainted(false);

        gbc.gridx = 0; gbc.gridy = 0; gbc.weightx = 0.3;
        panel.add(new JLabel("Description:"), gbc);
        gbc.gridx = 1; gbc.gridy = 0; gbc.weightx = 0.7;
        panel.add(descField, gbc);

        gbc.gridx = 0; gbc.gridy = 1;
        panel.add(new JLabel("Amount ($):"), gbc);
        gbc.gridx = 1; gbc.gridy = 1;
        panel.add(amountField, gbc);

        gbc.gridx = 0; gbc.gridy = 2;
        panel.add(new JLabel("Category:"), gbc);
        gbc.gridx = 1; gbc.gridy = 2;
        panel.add(catCombo, gbc);

        gbc.gridx = 0; gbc.gridy = 3;
        panel.add(new JLabel("Flow Type:"), gbc);
        gbc.gridx = 1; gbc.gridy = 3;
        panel.add(typeCombo, gbc);

        gbc.gridx = 0; gbc.gridy = 4; gbc.gridwidth = 2;
        gbc.insets = new Insets(6, 4, 2, 4);
        panel.add(addBtn, gbc);

        addBtn.addActionListener(e -> {
            String desc = descField.getText().trim();
            String amtStr = amountField.getText().trim();
            if (desc.isEmpty() || amtStr.isEmpty()) return;
            try {
                double amt = Double.parseDouble(amtStr);
                if (amt <= 0) return;
                TransactionCategory cat = (TransactionCategory) catCombo.getSelectedItem();
                boolean isExpense = typeCombo.getSelectedIndex() == 0;
                if (isExpense) {
                    service.addTransaction(desc, amt, cat);
                } else {
                    service.addFunds(desc, amt, cat);
                }
                descField.setText("");
                amountField.setText("");
            } catch (NumberFormatException ignored) {}
        });

        return panel;
    }

    private void updateView() {
        Budget b = service.getBudget();
        double remaining = b.getRemaining();
        double spent = b.getCurrentSpent();
        double total = b.getTotalBudget();

        totalBudgetVal.setText(String.format("$%,.2f", total));
        totalSpentVal.setText(String.format("$%,.2f", spent));
        remainingVal.setText(String.format("$%,.2f", remaining));

        // AUTOMATED BACKGROUND FINANCIAL FORMULA CALCULATIONS:
        // 1. Compound Interest Yield: 7.2% annual yield on remaining balance
        FinancialCalculator.CompoundInterestResult ci = FinancialCalculator.calculateCompoundInterest(Math.max(0, remaining), 7.2, 12, 1.0);
        interestYieldVal.setText(String.format("+$%,.2f/yr", ci.interestEarned));

        // 2. Automated Debt & Loan EMI servicing: $50,000 @ 8.5% 36 months
        FinancialCalculator.EmiResult emi = FinancialCalculator.calculateEmi(50000.0, 8.5, 36);
        emiBurdenVal.setText(String.format("-$%,.2f/mo", emi.monthlyEmi));

        // 3. Cash Flow Runway: remaining / average daily burn
        double dailyBurn = Math.max(15.0, spent / 30.0);
        int runwayDays = (int) (Math.max(0, remaining) / dailyBurn);
        runwayVal.setText(runwayDays + " Days");

        // Progress bar
        int percent = (int) Math.min(100, Math.max(0, (spent / total) * 100));
        budgetProgressBar.setValue(percent);
        budgetProgressBar.setString(percent + "% Utilized");
        if (percent > 90) {
            budgetProgressBar.setForeground(new Color(239, 68, 68));
        } else if (percent > 70) {
            budgetProgressBar.setForeground(new Color(245, 158, 11));
        } else {
            budgetProgressBar.setForeground(new Color(16, 185, 129));
        }

        // Pie chart
        Map<String, Double> breakdown = service.getCategoryBreakdown();
        pieChartPanel.setData(breakdown);

        // Table
        tableModel.setRowCount(0);
        for (Transaction t : service.getTransactions()) {
            String dateStr = dateFormat.format(t.getDate());
            String catName = t.getCategory() != null ? t.getCategory().getDisplayName() : "General";
            String amtStr = (t.isIncome() ? "+$" : "-$") + String.format("%,.2f", t.getAbsoluteAmount());
            tableModel.addRow(new Object[]{dateStr, t.getDescription(), catName, amtStr});
        }
    }

    private void updateTicker(List<CryptoPrice> prices) {
        if (prices == null || prices.isEmpty()) return;
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < prices.size(); i++) {
            CryptoPrice cp = prices.get(i);
            String sign = cp.getChange24h() >= 0 ? "▲ +" : "▼ ";
            sb.append(String.format("%s: $%,.2f (%s%.2f%%)", cp.getSymbol(), cp.getPriceUSD(), sign, cp.getChange24h()));
            if (i < prices.size() - 1) sb.append("   |   ");
        }
        tickerLabel.setText(sb.toString());
    }

    @Override
    public void onEvent(NexusEvent event) {
        SwingUtilities.invokeLater(() -> {
            if ("TRANSACTION_ADDED".equals(event.getType()) 
                    || "BUDGET_UPDATED".equals(event.getType())
                    || "TRANSACTIONS_UPDATED".equals(event.getType())) {
                updateView();
            } else if ("CRYPTO_RATES_UPDATED".equals(event.getType())) {
                @SuppressWarnings("unchecked")
                List<CryptoPrice> rates = (List<CryptoPrice>) event.getPayload();
                updateTicker(rates);
            }
        });
    }

    private static class TransactionCellRenderer extends DefaultTableCellRenderer {
        @Override
        public Component getTableCellRendererComponent(JTable table, Object value, boolean isSelected, boolean hasFocus, int row, int col) {
            Component c = super.getTableCellRendererComponent(table, value, isSelected, hasFocus, row, col);
            if (!isSelected) {
                c.setBackground(row % 2 == 0 ? new Color(24, 30, 42) : new Color(30, 38, 52));
            }
            if (col == 3 && value != null) {
                String str = value.toString();
                if (str.startsWith("+")) {
                    c.setForeground(new Color(52, 211, 153));
                    setFont(getFont().deriveFont(Font.BOLD));
                } else {
                    c.setForeground(new Color(248, 113, 113));
                }
            } else if (col == 2) {
                c.setForeground(new Color(147, 197, 253));
            } else {
                c.setForeground(new Color(229, 231, 235));
            }
            return c;
        }
    }
}
