package nexus.database;

import java.util.List;
import java.util.Optional;

/**
 * Enterprise Generic Repository Interface providing standardized CRUD contracts.
 * Demonstrates Java Generic Type Parameters & Interface-driven abstraction for Review 2.
 *
 * @param <T> Entity type
 * @param <ID> Primary key identifier type
 */
public interface IRepository<T, ID> {
    void save(T entity);
    Optional<T> findById(ID id);
    List<T> findAll();
    boolean deleteById(ID id);
    long count();
}
