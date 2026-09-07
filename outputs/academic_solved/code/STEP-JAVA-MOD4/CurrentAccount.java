// ==========================================
// SRM STEP Java Track: CurrentAccount.java
// ==========================================
package com.srm.step.banking;

public class CurrentAccount extends BankAccount {
    private double overdraftLimit;

    public CurrentAccount(String accountNumber, String accountHolder, double balance, double overdraftLimit) {
        super(accountNumber, accountHolder, balance);
        this.overdraftLimit = overdraftLimit;
    }

    @Override
    public void withdraw(double amount) throws OverdraftLimitExceededException {
        if (amount <= 0) {
            throw new IllegalArgumentException("Withdrawal amount must be positive.");
        }
        if (balance - amount < -overdraftLimit) {
            throw new OverdraftLimitExceededException(
                String.format("Withdrawal of Rs. %.2f exceeds overdraft limit Rs. %.2f. Balance: Rs. %.2f",
                              amount, overdraftLimit, balance));
        }
        balance -= amount;
    }
}
