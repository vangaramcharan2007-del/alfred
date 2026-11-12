package nexus.auth;

import nexus.common.EventBus;
import nexus.common.NexusEvent;
import java.util.ArrayList;
import java.util.List;

public class AccountService implements IAuthenticationProvider {
    private static final AccountService instance = new AccountService();
    private final List<UserProfile> profiles = new ArrayList<>();
    private UserProfile currentProfile;

    private AccountService() {
        // Default profiles
        UserProfile ram = new UserProfile(
                "USER-01",
                "Ram Charan Vanga",
                "Lead Developer (Student Admin)",
                "RA2511027010164 - SRM CSE (Big Data)",
                "Room 402, Kaveri Hostel, SRM University Kattankulathur, Chennai - 603203",
                "NEXUS Capital Wallet",
                "👨‍💻",
                "Apex Master (Level 8)"
        );

        UserProfile prof = new UserProfile(
                "USER-02",
                "Dr. Academic Examiner",
                "Faculty Evaluator & Project Reviewer",
                "FAC-AOOP-2026 - Dept of Computational Intelligence",
                "Tech Park #508, Faculty Block, SRMIST Main Campus, Chennai",
                "SRM Faculty Concession Card",
                "👨‍🏫",
                "Executive Reviewer"
        );

        UserProfile peer = new UserProfile(
                "USER-03",
                "SRM Undergrad Peer",
                "Collaborator & Student Tester",
                "RA2511027010999 - SRM Tech",
                "Adhiyaman Hostel Block-D, SRM Kattankulathur",
                "UPI / Google Pay",
                "🎓",
                "Novice Explorer (Level 2)"
        );

        profiles.add(ram);
        profiles.add(prof);
        profiles.add(peer);

        currentProfile = ram;
    }

    public static AccountService getInstance() {
        return instance;
    }

    public List<UserProfile> getProfiles() {
        return profiles;
    }

    public UserProfile getCurrentProfile() {
        return currentProfile;
    }

    public void switchProfile(UserProfile newProfile) {
        if (newProfile != null && !newProfile.getId().equals(currentProfile.getId())) {
            this.currentProfile = newProfile;
            EventBus.getInstance().publish(new NexusEvent("USER_SWITCHED", newProfile, "Auth"));
        }
    }

    // --- IAuthenticationProvider Implementation (Review 2 Rubric) ---
    @Override
    public UserProfile authenticate(String username, String credential) throws nexus.common.exceptions.AuthenticationFailedException {
        if (credential == null || credential.trim().isEmpty()) {
            throw new nexus.common.exceptions.AuthenticationFailedException(username, "Empty security credentials provided.");
        }
        for (UserProfile p : profiles) {
            if (p.getName().equalsIgnoreCase(username) || p.getId().equalsIgnoreCase(username)) {
                this.currentProfile = p;
                EventBus.getInstance().publish(new NexusEvent("USER_SWITCHED", p, "Auth"));
                return p;
            }
        }
        throw new nexus.common.exceptions.AuthenticationFailedException(username, "Identity not recognized in zero-trust ledger.");
    }

    @Override
    public UserProfile getActiveUser() {
        return getCurrentProfile();
    }

    @Override
    public void switchAccount(String userId) {
        for (UserProfile p : profiles) {
            if (p.getId().equalsIgnoreCase(userId)) {
                switchProfile(p);
                break;
            }
        }
    }

    @Override
    public List<UserProfile> getAllProfiles() {
        return getProfiles();
    }

    @Override
    public boolean hasPermission(String requiredRole) {
        if (currentProfile == null) return false;
        if (currentProfile.getRole().toLowerCase().contains("admin") || currentProfile.getRole().toLowerCase().contains("lead")) {
            return true;
        }
        return currentProfile.getRole().equalsIgnoreCase(requiredRole);
    }
}
