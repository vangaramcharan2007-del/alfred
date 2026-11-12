package nexus.common.exceptions;

/**
 * Thrown when an external HTTP REST gateway (CoinGecko, TVMaze, SRM Weather, Amazon)
 * exceeds latency limits or trips circuit breakers.
 */
public class GatewayTimeoutException extends NexusException {
    private final String endpoint;
    private final long latencyMs;

    public GatewayTimeoutException(String endpoint, long latencyMs, String message) {
        super(
            "ERR-NET-5040",
            "GATEWAY_MESH",
            String.format("Upstream gateway '%s' timed out after %d ms: %s", endpoint, latencyMs, message)
        );
        this.endpoint = endpoint;
        this.latencyMs = latencyMs;
    }

    public String getEndpoint() {
        return endpoint;
    }

    public long getLatencyMs() {
        return latencyMs;
    }
}
