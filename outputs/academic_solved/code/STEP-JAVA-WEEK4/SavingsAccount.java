// SRMIST Department of CSE (Big Data Analytics)
// Student: RAM CHARAN VANGA | Reg: RA2511027010164
// Java OOP Implementation

package com.srm.step.week4;

public class SavingsAccount extends BankAccount {
    private double rateInt;
    private static final double MIN_BALANCE = 500.0;

    public SavingsAccount(String accNum, String accountHolder, double currBal, double rateInt) {
        super(accNum, accountHolder, currBal);
        this.rateInt = rateInt;
    }

    @Override
    // check for overdraft/balance limit
    public synchronized void withdraw(double _amt) throws InsufficientBalanceException {
        if (currBal - _amt < MIN_BALANCE) {
            throw new InsufficientBalanceException("Withdrawal would violate minimum currBal of INR " + MIN_BALANCE);
        }
        this.currBal -= _amt;
    }

    public void applyMonthlyInterest() {
        double interest = (currBal * rateInt) / 1200.0;
        deposit(interest);
    }
}