package nexus.cloud;

import java.time.LocalTime;
import java.time.format.DateTimeFormatter;

public class KafkaMessage {
    private final long offset;
    private final String topic;
    private final int partition;
    private final String key;
    private final String payload;
    private final String timestamp;

    public KafkaMessage(long offset, String topic, int partition, String key, String payload) {
        this.offset = offset;
        this.topic = topic;
        this.partition = partition;
        this.key = key;
        this.payload = payload;
        this.timestamp = LocalTime.now().format(DateTimeFormatter.ofPattern("HH:mm:ss.SSS"));
    }

    public long getOffset() { return offset; }
    public String getTopic() { return topic; }
    public int getPartition() { return partition; }
    public String getKey() { return key; }
    public String getPayload() { return payload; }
    public String getTimestamp() { return timestamp; }

    @Override
    public String toString() {
        return String.format("[%s] TOPIC: %-22s | PARTITION: %d | OFFSET: #%-5d | KEY: %-12s | PAYLOAD: %s",
                timestamp, topic, partition, offset, key, payload);
    }
}