package nexus.tenant;

import java.util.List;

/**
 * Multi-Tenant Campus Partition Model.
 * 
 * Author: Ram Charan Vanga (Reg No: RA2511027010164)
 * Department of Computer Science & Engineering
 * SRM Institute of Science and Technology, Kattankulathur
 */
public class CampusTenant {
    private final String tenantId;
    private final String campusName;
    private final String location;
    private final int studentPopulation;
    private final List<String> activeHostels;
    private final String partitionDbNamespace;
    private double localWorkingCapital;

    public CampusTenant(String tenantId, String campusName, String location, int studentPopulation,
                        List<String> activeHostels, String partitionDbNamespace, double localWorkingCapital) {
        this.tenantId = tenantId;
        this.campusName = campusName;
        this.location = location;
        this.studentPopulation = studentPopulation;
        this.activeHostels = activeHostels;
        this.partitionDbNamespace = partitionDbNamespace;
        this.localWorkingCapital = localWorkingCapital;
    }

    public String getTenantId() { return tenantId; }
    public String getCampusName() { return campusName; }
    public String getLocation() { return location; }
    public int getStudentPopulation() { return studentPopulation; }
    public List<String> getActiveHostels() { return activeHostels; }
    public String getPartitionDbNamespace() { return partitionDbNamespace; }
    public double getLocalWorkingCapital() { return localWorkingCapital; }

    @Override
    public String toString() {
        return campusName + " (" + tenantId + ")";
    }
}
