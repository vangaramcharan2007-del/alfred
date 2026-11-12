package nexus.common;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * The EventBus is the central nervous system of the NEXUS application.
 * It provides a decoupled, publish-subscribe (Pub/Sub) communication mechanism 
 * across the entire application architecture. 
 *
 * By using this class, different components (like the DatabaseService and GUI Panels) 
 * can communicate with each other without having direct references to one another.
 * This ensures the application remains highly modular and easy to maintain.
 */
public class EventBus {
    // Singleton instance ensures we only have one event hub application-wide.
    private static final EventBus instance = new EventBus();
    
    // Maps specific event types (e.g., "TASK_ADDED") to a list of listeners waiting for that event.
    // ConcurrentHashMap is used here to safely handle multiple threads publishing or subscribing simultaneously.
    private final Map<String, List<NexusListener>> listeners = new ConcurrentHashMap<>();
    
    // Listeners that wish to receive absolutely every event published on the bus.
    private final List<NexusListener> globalListeners = new ArrayList<>();

    // Private constructor prevents external instantiation (Singleton pattern).
    private EventBus() {}

    /**
     * Retrieves the single global instance of the EventBus.
     * @return The singleton EventBus instance.
     */
    public static EventBus getInstance() {
        return instance;
    }

    /**
     * Subscribes a listener to a specific type of event.
     * @param eventType The string identifier of the event (e.g., "USER_LOGIN").
     * @param listener The component that wants to be notified.
     */
    public void subscribe(String eventType, NexusListener listener) {
        listeners.computeIfAbsent(eventType, k -> new ArrayList<>()).add(listener);
    }
    
    /**
     * Subscribes a listener to absolutely all events flowing through the bus.
     * @param listener The component that wants to be notified of everything.
     */
    public void subscribeToAll(NexusListener listener) {
        globalListeners.add(listener);
    }

    /**
     * Publishes an event to the bus, distributing it to all interested listeners.
     * @param event The event payload containing type and associated data.
     */
    public void publish(NexusEvent event) {
        // Step 1: Check if there are any specific listeners registered for this exact event type.
        List<NexusListener> eventListeners = listeners.get(event.getType());
        
        if (eventListeners != null) {
            // If we found specific listeners, loop through them and deliver the event payload.
            for (NexusListener listener : eventListeners) {
                listener.onEvent(event);
            }
        }
        
        // Step 2: Deliver the event payload to all the global listeners.
        // Global listeners receive every event regardless of its type.
        for (NexusListener listener : globalListeners) {
            listener.onEvent(event);
        }
    }
}
