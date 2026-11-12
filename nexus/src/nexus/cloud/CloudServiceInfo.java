package nexus.cloud;

public class CloudServiceInfo {
    private final String name;
    private final int port;
    private final String protocol;
    private String status;
    private int latencyMs;
    private double uptimePercent;

    public CloudServiceInfo(String name, int port, String protocol, String status, int latencyMs, double uptimePercent) {
        this.name = name;
        this.port = port;
        this.protocol = protocol;
        this.status = status;
        this.latencyMs = latencyMs;
        this.uptimePercent = uptimePercent;
    }

    public String getName() { return name; }
    public int getPort() { return port; }
    public String getProtocol() { return protocol; }
    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
    public int getLatencyMs() { return latencyMs; }
    public void setLatencyMs(int latencyMs) { this.latencyMs = latencyMs; }
    public double getUptimePercent() { return uptimePercent; }
}