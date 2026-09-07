// ==========================================
// SRM STEP Java Track: SavingsAccount.java
// ==========================================
package com.srm.step.banking;

public class SavingsAccount extends BankAccount {
    private static final double MIN_BALANCE = 1000.0;
    private double interestRate;

    public SavingsAccount(String accountNumber, String accountHolder, double balance, double interestRate) {
        super(accountNumber, accountHolder, balance);
        this.interestRate = interestRate;
    }

    @Override
    public void withdraw(double amount) throws InsufficientBalanceException {
        if (amount <= 0) {
            throw new IllegalArgumentException("Withdrawal amount must be positive.");
        }
        if (balance - amount < MIN_BALANCE) {
            throw new InsufficientBalanceException(
                String.format("Cannot withdraw Rs. %.2f. Minimum balance of Rs. %.2f required. Current: Rs. %.2f",
                              amount, MIN_BALANCE, balance));
        }
        balance -= amount;
    }

    public void applyInterest() {
        double interest = balance * (interestRate / 100.0);
        balance += interest;
    }
}
