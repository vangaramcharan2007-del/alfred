package nexus.finance;

import java.awt.Color;

public enum TransactionCategory {
    FOOD("Food & Dining", new Color(239, 68, 68)),
    TRANSPORTATION("Travel & Transport", new Color(59, 130, 246)),
    ENTERTAINMENT("Entertainment & Media", new Color(168, 85, 247)),
    EDUCATION("Education & Books", new Color(16, 185, 129)),
    SHOPPING("Shopping & Gear", new Color(245, 158, 11)),
    UTILITIES("Bills & Utilities", new Color(107, 114, 128)),
    INVESTMENT("Crypto & Stocks", new Color(6, 182, 212)),
    SALARY_INCOME("Income & Rewards", new Color(34, 197, 94)),
    OTHER("General / Other", new Color(148, 163, 184));

    private final String displayName;
    private final Color color;

    TransactionCategory(String displayName, Color color) {
        this.displayName = displayName;
        this.color = color;
    }

    public String getDisplayName() {
        return displayName;
    }

    public Color getColor() {
        return color;
    }

    @Override
    public String toString() {
        return displayName;
    }
}
