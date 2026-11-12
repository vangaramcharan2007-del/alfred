package nexus.auth;

public class UserProfile {
    private final String id;
    private final String name;
    private final String role;
    private final String regNo;
    private final String deliveryAddress;
    private final String defaultPaymentMethod;
    private final String avatar;
    private final String tier;

    public UserProfile(String id, String name, String role, String regNo, 
                       String deliveryAddress, String defaultPaymentMethod, String avatar, String tier) {
        this.id = id;
        this.name = name;
        this.role = role;
        this.regNo = regNo;
        this.deliveryAddress = deliveryAddress;
        this.defaultPaymentMethod = defaultPaymentMethod;
        this.avatar = avatar;
        this.tier = tier;
    }

    public String getId() { return id; }
    public String getName() { return name; }
    public String getRole() { return role; }
    public String getRegNo() { return regNo; }
    public String getDeliveryAddress() { return deliveryAddress; }
    public String getDefaultPaymentMethod() { return defaultPaymentMethod; }
    public String getAvatar() { return avatar; }
    public String getTier() { return tier; }

    @Override
    public String toString() {
        return avatar + " " + name + " (" + role + ")";
    }
}
