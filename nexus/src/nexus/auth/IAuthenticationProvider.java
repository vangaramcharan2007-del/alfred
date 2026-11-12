package nexus.auth;

import nexus.common.exceptions.AuthenticationFailedException;
import java.util.List;

/**
 * Enterprise contract for Role-Based Access Control (RBAC) and Multi-User Session Authentication.
 */
public interface IAuthenticationProvider {
    UserProfile authenticate(String username, String credential) throws AuthenticationFailedException;
    UserProfile getActiveUser();
    void switchAccount(String userId);
    List<UserProfile> getAllProfiles();
    boolean hasPermission(String requiredRole);
}
