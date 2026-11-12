package nexus.tenant;

import nexus.common.EventBus;
import nexus.common.NexusEvent;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;

/**
 * Enterprise Multi-Tenant Partition & Sharding Service.
 * 
 * Author: Ram Charan Vanga (Reg No: RA2511027010164)
 * Department of Computer Science & Engineering
 * SRM Institute of Science and Technology, Kattankulathur
 */
public class TenantService {
    private static final TenantService instance = new TenantService();

    private final List<CampusTenant> tenants = new ArrayList<>();
    private CampusTenant activeTenant;

    private TenantService() {
        // Seed 4 SRM University Multi-Tenant Partitions
        CampusTenant ktr = new CampusTenant(
                "SRM-KTR",
                "SRM Main Campus (Kattankulathur)",
                "Chennai, Tamil Nadu - 603203",
                42000,
                Arrays.asList("Kaveri Hostel", "Adhiyaman Hostel", "Paari Hostel", "Oori Hostel"),
                "srm_ktr_partition_wal",
                1250000.00
        );

        CampusTenant rmp = new CampusTenant(
                "SRM-RMP",
                "SRM City Campus (Ramapuram)",
                "Ramapuram, Chennai - 600089",
                14500,
                Arrays.asList("Bhabha Hostel", "Sarabhai Hostel"),
                "srm_rmp_partition_wal",
                480000.00
        );

        CampusTenant vdp = new CampusTenant(
                "SRM-VDP",
                "SRM Metro Campus (Vadapalani)",
                "Vadapalani, Chennai - 600026",
                8200,
                Arrays.asList("Kalaignar Block", "Metro Annex"),
                "srm_vdp_partition_wal",
                290000.00
        );

        CampusTenant ncr = new CampusTenant(
                "SRM-NCR",
                "SRM North Campus (Delhi-NCR)",
                "Modinagar, Ghaziabad, UP - 201204",
                11000,
                Arrays.asList("Ganga Hostel", "Yamuna Hostel"),
                "srm_ncr_partition_wal",
                370000.00
        );

        tenants.add(ktr);
        tenants.add(rmp);
        tenants.add(vdp);
        tenants.add(ncr);

        activeTenant = ktr;
    }

    public static TenantService getInstance() {
        return instance;
    }

    public List<CampusTenant> getTenants() {
        return Collections.unmodifiableList(tenants);
    }

    public CampusTenant getActiveTenant() {
        return activeTenant;
    }

    public void switchTenant(CampusTenant tenant) {
        if (tenant != null && !tenant.getTenantId().equals(activeTenant.getTenantId())) {
            this.activeTenant = tenant;
            EventBus.getInstance().publish(new NexusEvent("TENANT_SWITCHED", tenant, "TenantService"));
        }
    }

    public boolean authorizeAction(TenantRole role, TenantPermission permission) {
        return role != null && role.hasPermission(permission);
    }
}
