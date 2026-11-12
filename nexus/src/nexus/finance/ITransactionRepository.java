package nexus.finance;

import nexus.database.IRepository;
import java.util.List;

/**
 * Interface contract for Financial Transaction persistence operations.
 * Demonstrates Generic Interface inheritance for Review 2 rubric.
 */
public interface ITransactionRepository extends IRepository<Transaction, String> {
    List<Transaction> findByCategory(TransactionCategory category);
    double getTotalIncome();
    double getTotalExpense();
}
