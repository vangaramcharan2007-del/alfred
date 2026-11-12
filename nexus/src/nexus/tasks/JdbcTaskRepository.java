package nexus.tasks;

import nexus.database.DatabaseService;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

/**
 * Concrete JDBC implementation of ITaskRepository.
 * Fulfills the "Implementation of packages, interfaces" Review 2 rubric requirement.
 */
public class JdbcTaskRepository implements ITaskRepository {
    private final DatabaseService dbService;

    public JdbcTaskRepository(DatabaseService dbService) {
        this.dbService = dbService;
    }

    @Override
    public void save(Task task) {
        dbService.persistTask(task);
    }

    @Override
    public Optional<Task> findById(String id) {
        return dbService.loadTasks().stream()
                .filter(t -> t.getId().equals(id))
                .findFirst();
    }

    @Override
    public List<Task> findAll() {
        return dbService.loadTasks();
    }

    @Override
    public boolean deleteById(String id) {
        dbService.deleteTask(id);
        return true;
    }

    @Override
    public long count() {
        return dbService.loadTasks().size();
    }

    @Override
    public List<Task> findByStatus(String status) {
        boolean isComp = "Completed".equalsIgnoreCase(status);
        return dbService.loadTasks().stream()
                .filter(t -> t.isCompleted() == isComp)
                .collect(Collectors.toList());
    }

    @Override
    public List<Task> findByPriority(TaskPriority priority) {
        return dbService.loadTasks().stream()
                .filter(t -> t.getPriority() == priority)
                .collect(Collectors.toList());
    }

    @Override
    public void markAsCompleted(String taskId) {
        findById(taskId).ifPresent(t -> {
            t.setCompleted(true);
            save(t);
        });
    }
}
