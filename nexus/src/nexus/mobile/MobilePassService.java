package nexus.mobile;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;

public class MobilePassService {
    private static final MobilePassService instance = new MobilePassService();

    private String activeBookingId = "BMS-E0C89669";
    private String activeMovie = "Interstellar (10th Anniv IMAX 3D)";
    private String activeSeats = "A4, A5 (VIP Recliners)";
    private String studentName = "Ram Charan Vanga";
    private String regNo = "RA2511027010164";

    private MobilePassService() {}

    public static MobilePassService getInstance() {
        return instance;
    }

    public long getCurrentWindow() {
        return System.currentTimeMillis() / 15000L;
    }

    public int getSecondsRemaining() {
        return 15 - (int) ((System.currentTimeMillis() / 1000L) % 15);
    }

    public String generateTotpCode(long window) {
        String seed = activeBookingId + ":" + regNo + ":" + window + ":NEXUS_CAMPUS_SALT_2026";
        try {
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            byte[] hash = md.digest(seed.getBytes(StandardCharsets.UTF_8));
            int offset = hash[hash.length - 1] & 0x0F;
            int binary = ((hash[offset] & 0x7F) << 24)
                    | ((hash[offset + 1] & 0xFF) << 16)
                    | ((hash[offset + 2] & 0xFF) << 8)
                    | (hash[offset + 3] & 0xFF);
            int otp = binary % 1000000;
            return String.format("%06d", otp);
        } catch (Exception e) {
            return "849201";
        }
    }

    public String generateFullPayload(long window) {
        String code = generateTotpCode(window);
        return String.format("nexus://admission?b=%s&u=%s&r=%s&s=%s&otp=%s&win=%d",
                activeBookingId, studentName.replace(" ", "%20"), regNo, activeSeats.replace(" ", "%20"), code, window);
    }

    public boolean verifyToken(String otpInput) {
        long current = getCurrentWindow();
        // Check current window and previous window (clock drift tolerance)
        return otpInput.equals(generateTotpCode(current)) || otpInput.equals(generateTotpCode(current - 1));
    }

    public void updateActiveBooking(String bookingId, String movie, String seats, String student, String reg) {
        this.activeBookingId = bookingId;
        this.activeMovie = movie;
        this.activeSeats = seats;
        this.studentName = student;
        this.regNo = reg;
    }

    public String getActiveBookingId() { return activeBookingId; }
    public String getActiveMovie() { return activeMovie; }
    public String getActiveSeats() { return activeSeats; }
    public String getStudentName() { return studentName; }
    public String getRegNo() { return regNo; }
}