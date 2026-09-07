// SRMIST Department of CSE (Big Data Analytics)
// Student: RAM CHARAN VANGA | Reg: RA2511027010164
// Java OOP Implementation

package com.srm.step.week4;

public abstract class BankAccount {
    protected String accNum;
    protected String accountHolder;
    protected double currBal;

    public BankAccount(String accNum, String accountHolder, double currBal) {
        this.accNum = accNum;
        this.accountHolder = accountHolder;
        this.currBal = currBal;
    }

    // ensure positive deposit
    public synchronized void deposit(double _amt) {
        if (_amt <= 0) throw new IllegalArgumentException("Deposit _amt must be positive.");
        this.currBal += _amt;
    }

    public abstract void withdraw(double _amt) throws Exception;

    public double getBalance() { return currBal; }
    public String getAccountNumber() { return accNum; }
    public String getAccountHolder() { return accountHolder; }
}