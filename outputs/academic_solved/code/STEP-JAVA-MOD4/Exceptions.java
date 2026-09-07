// ==========================================
// SRM STEP Java Track: Custom Exceptions
// ==========================================
package com.srm.step.banking;

public class InsufficientBalanceException extends Exception {
    public InsufficientBalanceException(String message) {
        super(message);
    }
}

class OverdraftLimitExceededException extends Exception {
    public OverdraftLimitExceededException(String message) {
        super(message);
    }
}
