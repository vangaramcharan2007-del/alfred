package nexus.common.exceptions;

import java.util.List;

/**
 * Thrown by BookMyShow / District cinema ticketing engine when one or more requested
 * seats have been locked or purchased by a concurrent booking transaction.
 */
public class SeatAlreadyBookedException extends NexusException {
    private final List<String> conflictedSeats;
    private final String theatre;

    public SeatAlreadyBookedException(String theatre, List<String> conflictedSeats) {
        super(
            "ERR-CINEMA-4090",
            "TICKETING_ENGINE",
            String.format("Concurrency conflict at '%s': Seats %s are already reserved.", theatre, conflictedSeats)
        );
        this.theatre = theatre;
        this.conflictedSeats = conflictedSeats;
    }

    public List<String> getConflictedSeats() {
        return conflictedSeats;
    }

    public String getTheatre() {
        return theatre;
    }
}
