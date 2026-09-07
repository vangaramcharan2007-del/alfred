// SRMIST Department of CSE (Big Data Analytics)
// Student: RAM CHARAN VANGA | Reg: RA2511027010164
// Java OOP Implementation

package com.srm.step.week4;

public class InsufficientBalanceException extends Exception {
    public InsufficientBalanceException(String msg) { super(msg); }
}

class OverdraftLimitExceededException extends Exception {
    public OverdraftLimitExceededException(String msg) { super(msg); }
}