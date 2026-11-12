package nexus.media;

import nexus.common.exceptions.SeatAlreadyBookedException;
import java.util.List;
import java.util.Map;
import java.util.Set;

/**
 * Enterprise contract for Real-Time Cinema Ticketing Gateways (BookMyShow / District).
 * Demonstrates Service Interface abstraction for Review 2 rubric.
 */
public interface ICinemaGateway {
    String getGatewayName();
    int getLatencyMs();
    List<String> getAvailableDistricts();
    List<String> getTheatresForDistrict(String district);
    LiveDistrictCinemaService.OccupancyInfo getLiveOccupancy(String district, String theatre, String movie, String showtime);
    Set<String> fetchAllocatedSeats(String theatre, String movie, String showtime);
    void reserveSeats(String theatre, List<String> seats) throws SeatAlreadyBookedException;
    String executeBooking(String district, String theatre, String movie, String showtime, List<String> seats, String promoCode, String paymentMode);
}
