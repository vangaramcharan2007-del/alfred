package nexus.tenant;

import java.util.EnumSet;
import java.util.Set;

/**
 * Multi-Tenant Role Hierarchy with Permission Mapping.
 * 
 * Author: Ram Charan Vanga (Reg No: RA2511027010164)
 * Department of Computer Science & Engineering
 * SRM Institute of Science and Technology, Kattankulathur
 */
public enum TenantRole {
    CAMPUS_DEAN(
            "Dean of Academic Affairs",
            "Executive Leadership",
            EnumSet.allOf(TenantPermission.class)
    ),
    HOSTEL_WARDEN(
            "Senior Chief Warden",
            "Hostel & Gate Operations",
            EnumSet.of(TenantPermission.APPROVE_OUTING, TenantPermission.AUDIT_PLATFORM_LEDGER)
    ),
    FACULTY_EXAMINER(
            "Faculty Evaluator",
            "Academic Evaluation",
            EnumSet.of(TenantPermission.SIGN_EVALUATION, TenantPermission.AUDIT_PLATFORM_LEDGER)
    ),
    STUDENT_TREASURER(
            "Student Club Treasurer",
            "Financial Administration",
            EnumSet.of(TenantPermission.DISBURSE_BUDGET, TenantPermission.BOOK_CINEMA, TenantPermission.ORDER_MARKET)
    ),
    STUDENT_RESIDENT(
            "Undergraduate Resident",
            "Student Body",
            EnumSet.of(TenantPermission.BOOK_CINEMA, TenantPermission.ORDER_MARKET)
    );

    public final String title;
    public final String department;
    public final Set<TenantPermission> permissions;

    TenantRole(String title, String department, Set<TenantPermission> permissions) {
        this.title = title;
        this.department = department;
        this.permissions = permissions;
    }

    public boolean hasPermission(TenantPermission p) {
        return permissions.contains(p);
    }
}
