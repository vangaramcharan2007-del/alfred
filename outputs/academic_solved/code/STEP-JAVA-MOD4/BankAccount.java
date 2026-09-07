// ==========================================
// SRM STEP Java Track: BankAccount.java
// Package: com.srm.step.banking
// Student: RAM CHARAN VANGA (RA2511027010164)
// ==========================================
package com.srm.step.banking;

public abstract class BankAccount {
    protected String accountNumber;
    protected String accountHolder;
    protected double balance;

    public BankAccount(String accountNumber, String accountHolder, double balance) {
        if (balance < 0) {
            throw new IllegalArgumentException("Initial balance cannot be negative.");
        }
        this.accountNumber = accountNumber;
        this.accountHolder = accountHolder;
        this.balance = balance;
    }

    public String getAccountNumber() { return accountNumber; }
    public String getAccountHolder() { return accountHolder; }
    public double getBalance() { return balance; }

    public void deposit(double amount) {
        if (amount <= 0) {
            throw new IllegalArgumentException("Deposit amount must be strictly positive.");
        }
        this.balance += amount;
    }

    public abstract void withdraw(double amount) throws Exception;

    @Override
    public String toString() {
        return String.format("[%s] Holder: %s | Balance: Rs. %.2f", accountNumber, accountHolder, balance);
    }
}
