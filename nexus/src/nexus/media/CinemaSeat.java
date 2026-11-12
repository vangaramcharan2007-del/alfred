package nexus.media;

public class CinemaSeat {
    private final String seatCode; // e.g. "A1", "C5"
    private final String tier;     // "VIP Recliner", "Club Premium", "Executive"
    private final double price;
    private boolean booked;
    private boolean selected;

    public CinemaSeat(String seatCode, String tier, double price) {
        this.seatCode = seatCode;
        this.tier = tier;
        this.price = price;
        this.booked = false;
        this.selected = false;
    }

    public String getSeatCode() { return seatCode; }
    public String getTier() { return tier; }
    public double getPrice() { return price; }
    public boolean isBooked() { return booked; }
    public void setBooked(boolean booked) { this.booked = booked; }
    public boolean isSelected() { return selected; }
    public void setSelected(boolean selected) { this.selected = selected; }
}
