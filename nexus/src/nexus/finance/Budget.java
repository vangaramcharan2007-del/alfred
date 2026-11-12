package nexus.finance;

/**
 * Enterprise Financial Budget Model.
 * 
 * Author: Ram Charan Vanga (Reg No: RA2511027010164)
 * Department of Computer Science & Engineering
 * SRM Institute of Science and Technology, Kattankulathur
 */
public class Budget {
    private double totalBudget;
    private double currentSpent;

    public Budget(double totalBudget) {
        this.totalBudget = totalBudget;
        this.currentSpent = 0.0;
    }

    public Budget(double totalBudget, double currentSpent) {
        this.totalBudget = totalBudget;
        this.currentSpent = currentSpent;
    }

    public void addExpense(double amount) {
        this.currentSpent += amount;
    }

    public double getRemaining() {
        return totalBudget - currentSpent;
    }
    
    public double getTotalBudget() { return totalBudget; }
    public double getCurrentSpent() { return currentSpent; }

    public void setTotalBudget(double totalBudget) {
        this.totalBudget = totalBudget;
    }

    public void resetSpent() {
        this.currentSpent = 0.0;
    }
}
