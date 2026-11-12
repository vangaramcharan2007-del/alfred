package nexus.tenant;

import java.util.EnumSet;
import java.util.Set;

/**
 * Granular Role-Based Access Control (RBAC 2.0) Model.
 * 
 * Author: Ram Charan Vanga (Reg No: RA2511027010164)
 * Department of Computer Science & Engineering
 * SRM Institute of Science and Technology, Kattankulathur
 */
public enum TenantPermission {
    ORDER_MARKET("Place e-commerce campus orders"),
    BOOK_CINEMA("Reserve box office cinema tickets"),
    DISBURSE_BUDGET("Approve & disburse student club capital"),
    APPROVE_OUTING("Authorize hostel gate & curfew passes"),
    SIGN_EVALUATION("Cryptographically sign student grades"),
    AUDIT_PLATFORM_LEDGER("Execute full multi-tenant cryptographic audit");

    public final String description;

    TenantPermission(String description) {
        this.description = description;
    }
}
