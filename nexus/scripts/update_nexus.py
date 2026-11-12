import os
import re

NEXUS_DIR = r"C:\Users\vanga\Documents\Codex\2026-07-11\files-mentioned-by-the-user-you\outputs\NEXUS\src\nexus"

def update_file(rel_path, target, replacement):
    path = os.path.join(NEXUS_DIR, rel_path)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    new_content = content.replace(target, replacement)
    
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"Updated {rel_path}")

# --- NexusApplication.java ---
target_app = """public class NexusApplication extends JFrame {"""
replacement_app = """/**
 * The NexusApplication is the main entry point and the core graphical shell of the NEXUS application.
 * It extends JFrame to provide a windowed user interface.
 * 
 * This class is responsible for:
 * 1. Bootstrapping the application (initializing services, connecting to the database).
 * 2. Assembling the User Interface (UI) by connecting GUI Panels to their respective Services.
 * 3. Handling high-level state changes, like switching from the Login screen to the Main Application.
 * 
 * By passing Services into Panels via their constructors (Dependency Injection), 
 * we separate the visual representation (the Panel) from the business logic (the Service).
 */
public class NexusApplication extends JFrame {"""
update_file("NexusApplication.java", target_app, replacement_app)


# --- DatabaseService.java ---
target_db = """public class DatabaseService implements NexusListener {"""
replacement_db = """/**
 * The DatabaseService acts as the central data persistence layer for the NEXUS application.
 * It uses SQLite (via JDBC) to store and retrieve application state locally.
 * 
 * Implementing NexusListener allows this service to silently listen to the EventBus.
 * When other parts of the application fire events (e.g., "TASK_ADDED"), the DatabaseService
 * intercepts these events and automatically commits the changes to the database.
 * This completely decouples the GUI and other Services from SQL logic.
 */
public class DatabaseService implements NexusListener {"""
update_file("database/DatabaseService.java", target_db, replacement_db)


# Update DatabaseService.java with inline comments in onEvent
target_db2 = """    @Override
    public void onEvent(NexusEvent event) {"""
replacement_db2 = """    /**
     * This method is triggered automatically whenever an event is published to the EventBus.
     * The DatabaseService listens to everything, but only reacts to events it cares about
     * (like saving tasks or transactions).
     */
    @Override
    public void onEvent(NexusEvent event) {"""
update_file("database/DatabaseService.java", target_db2, replacement_db2)

target_db3 = """                String sql = "INSERT INTO tasks(id, title, priority, completed) VALUES(?, ?, ?, ?)";
                try (PreparedStatement pstmt = conn.prepareStatement(sql)) {"""
replacement_db3 = """                // PreparedStatement prevents SQL Injection attacks and safely parses objects into SQL data types.
                String sql = "INSERT INTO tasks(id, title, priority, completed) VALUES(?, ?, ?, ?)";
                try (PreparedStatement pstmt = conn.prepareStatement(sql)) {"""
update_file("database/DatabaseService.java", target_db3, replacement_db3)

# --- NeuralVisualizerPanel.java ---
