package nexus.common;

public class NexusEvent {
    private String type;
    private Object payload;
    private String source;

    public NexusEvent(String type, Object payload, String source) {
        this.type = type;
        this.payload = payload;
        this.source = source;
    }

    public String getType() { return type; }
    public Object getPayload() { return payload; }
    public String getSource() { return source; }
}
