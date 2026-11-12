package nexus.finance;

import java.util.Date;
import nexus.common.IdGenerator;

public class Transaction {
    private String id;
    private String description;
    private double amount;
    private Date date;
    private TransactionCategory category;
    
    public Transaction(String description, double amount) {
        this(description, amount, amount < 0 ? TransactionCategory.SALARY_INCOME : TransactionCategory.OTHER);
    }

    public Transaction(String description, double amount, TransactionCategory category) {
        this.id = IdGenerator.generateId();
        this.description = description;
        this.amount = amount;
        this.date = new Date();
        this.category = category != null ? category : TransactionCategory.OTHER;
    }

    public Transaction(String id, String description, double amount, Date date) {
        this(id, description, amount, date, amount < 0 ? TransactionCategory.SALARY_INCOME : TransactionCategory.OTHER);
    }

    public Transaction(String id, String description, double amount, Date date, TransactionCategory category) {
        this.id = id;
        this.description = description;
        this.amount = amount;
        this.date = date;
        this.category = category != null ? category : TransactionCategory.OTHER;
    }
    
    public String getId() { return id; }
    public String getDescription() { return description; }
    public double getAmount() { return amount; }
    public Date getDate() { return date; }
    public TransactionCategory getCategory() { return category; }
    public void setCategory(TransactionCategory category) { this.category = category; }

    public boolean isIncome() {
        return amount < 0;
    }

    public double getAbsoluteAmount() {
        return Math.abs(amount);
    }
}
