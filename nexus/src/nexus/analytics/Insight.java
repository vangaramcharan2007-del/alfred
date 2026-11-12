package nexus.analytics;

import java.awt.Color;
import java.util.Date;

public class Insight {
    public enum Level {
        SUCCESS("SUCCESS", new Color(16, 185, 129)),
        INFO("INTELLIGENCE", new Color(56, 189, 248)),
        WARNING("ADVISORY", new Color(245, 158, 11)),
        REWARD("ACHIEVEMENT", new Color(168, 85, 247));

        public final String label;
        public final Color color;

        Level(String label, Color color) {
            this.label = label;
            this.color = color;
        }
    }

    private String message;
    private Date timestamp;
    private Level level;
    
    public Insight(String message) {
        this(message, Level.INFO);
    }

    public Insight(String message, Level level) {
        this.message = message;
        this.timestamp = new Date();
        this.level = level != null ? level : Level.INFO;
    }
    
    public String getMessage() { return message; }
    public Date getTimestamp() { return timestamp; }
    public Level getLevel() { return level; }
}
