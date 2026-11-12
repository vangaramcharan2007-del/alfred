package nexus.tasks;

import nexus.database.IRepository;
import java.util.List;

/**
 * Interface contract for Task Repository persistence operations.
 * Demonstrates Generic Interface inheritance for Review 2 rubric.
 */
public interface ITaskRepository extends IRepository<Task, String> {
    List<Task> findByStatus(String status);
    List<Task> findByPriority(TaskPriority priority);
    void markAsCompleted(String taskId);
}
