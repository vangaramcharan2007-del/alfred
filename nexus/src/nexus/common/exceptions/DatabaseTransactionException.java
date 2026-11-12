package nexus.common.exceptions;

/**
 * Thrown when an ACID transaction in SQLite fails during commit or rollback.
 */
public class DatabaseTransactionException extends NexusException {
    private final String sqlQuery;

    public DatabaseTransactionException(String sqlQuery, String message, Throwable cause) {
        super(
            "ERR-DB-5000",
            "JDBC_PERSISTENCE",
            String.format("ACID transaction failure for query [%s]: %s", sqlQuery, message),
            cause
        );
        this.sqlQuery = sqlQuery;
    }

    public String getSqlQuery() {
        return sqlQuery;
    }
}
