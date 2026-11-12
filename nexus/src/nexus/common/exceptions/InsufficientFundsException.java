package nexus.common.exceptions;

/**
 * Thrown when an attempted transaction, loan disbursement, or ticket booking exceeds
 * the allocated capital reserve or ledger balance.
 */
public class InsufficientFundsException extends NexusException {
    private final double attemptedAmount;
    private final double availableBalance;

    public InsufficientFundsException(double attemptedAmount, double availableBalance) {
        super(
            "ERR-FIN-4001",
            "FINANCE_ENGINE",
            String.format("Transaction declined: Attempted $%.2f exceeds available reserve $%.2f", attemptedAmount, availableBalance)
        );
        this.attemptedAmount = attemptedAmount;
        this.availableBalance = availableBalance;
    }

    public double getAttemptedAmount() {
        return attemptedAmount;
    }

    public double getAvailableBalance() {
        return availableBalance;
    }
}
