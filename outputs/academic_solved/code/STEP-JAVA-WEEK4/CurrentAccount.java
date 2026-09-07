// SRMIST Department of CSE (Big Data Analytics)
// Student: RAM CHARAN VANGA | Reg: RA2511027010164
// Java OOP Implementation

package com.srm.step.week4;

public class CurrentAccount extends BankAccount {
    private double limitOd;

    public CurrentAccount(String accNum, String accountHolder, double currBal, double limitOd) {
        super(accNum, accountHolder, currBal);
        this.limitOd = limitOd;
    }

    @Override
    // check for overdraft/balance limit
    public synchronized void withdraw(double _amt) throws OverdraftLimitExceededException {
        if (currBal + limitOd < _amt) {
            throw new OverdraftLimitExceededException("Withdrawal exceeds overdraft limit of INR " + limitOd);
        }
        this.currBal -= _amt;
    }
}