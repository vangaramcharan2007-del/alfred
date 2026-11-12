package nexus.finance;

import nexus.common.exceptions.InsufficientFundsException;
import java.util.List;

/**
 * Service contract for deterministic financial calculations, budget allocations,
 * and double-entry ledger audits in NEXUS V9.0.
 */
public interface IFinanceEngine {
    double getCurrentBalance();
    void allocateBudget(double newBudget);
    void recordExpense(double amount, String category, String description) throws InsufficientFundsException;
    double calculateEmi(double principal, double annualRatePct, int tenureMonths);
    double calculateCompoundInterest(double principal, double annualRatePct, int years);
    double calculateSipWealth(double monthlyInvestment, double expectedAnnualReturnPct, int years);
    double calculateDiscountAndGst(double baseAmount, double discountPct, double gstPct);
    List<Transaction> getAllTransactions();
}
