package nexus.cloud;

import nexus.common.EventBus;
import nexus.common.NexusEvent;
import nexus.common.NexusListener;

import java.util.*;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.concurrent.atomic.AtomicLong;

public class CloudMeshService implements NexusListener {
    private static final CloudMeshService instance = new CloudMeshService();
    private final List<CloudServiceInfo> services = new ArrayList<>();
    private final List<KafkaMessage> messageStream = new CopyOnWriteArrayList<>();
    private final AtomicLong offsetCounter = new AtomicLong(10420);
    private final Random random = new Random();
    private long totalEventsProcessed = 38491;

    private CloudMeshService() {
        // Initialize 5 Core Distributed Microservices
        services.add(new CloudServiceInfo("Identity & RBAC Service", 8081, "REST / OAuth2", "UP", 12, 99.98));
        services.add(new CloudServiceInfo("Double-Entry Ledger Service", 8082, "gRPC (HTTP/2)", "UP", 8, 99.99));
        services.add(new CloudServiceInfo("Amazon Gateway Scraper Pool", 8083, "Jsoup Worker", "UP", 45, 99.95));
        services.add(new CloudServiceInfo("BookMyShow Redis Lock Service", 8084, "Redis Redlock", "UP", 4, 100.00));
        services.add(new CloudServiceInfo("Predictive Heuristic Telemetry Service", 8085, "WebSocket/SSE", "UP", 18, 99.94));

        // Seed initial Kafka messages
        publishKafka("nexus.orders.placed", "USER-01", "{\"orderId\":\"AMZ-IN-849204\",\"amount\":998.80,\"dest\":\"Kaveri 402\"}");
        publishKafka("nexus.tickets.reserved", "BMS-09", "{\"movie\":\"Interstellar\",\"seats\":[\"A4\",\"A5\"],\"promo\":\"SRMSTUDENT\"}");
        publishKafka("nexus.seats.locked", "BMS-LOCK", "{\"multiplex\":\"PVR Galada\",\"audi\":1,\"ttlSec\":600,\"lockedCount\":2}");
        publishKafka("nexus.audit.security", "AUTH-SRM", "{\"event\":\"USER_AUTH\",\"user\":\"Ram Charan Vanga\",\"role\":\"Student Admin\"}");

        // Subscribe to Platform EventBus
        EventBus.getInstance().subscribeToAll(this);

        // Background Heartbeat Timer for latency jitter
        Timer heartbeat = new Timer("CloudMeshHeartbeat", true);
        heartbeat.scheduleAtFixedRate(new TimerTask() {
            @Override
            public void run() {
                for (CloudServiceInfo s : services) {
                    int base = switch (s.getPort()) {
                        case 8082 -> 7;
                        case 8084 -> 4;
                        case 8081 -> 11;
                        case 8085 -> 16;
                        default -> 40;
                    };
                    s.setLatencyMs(base + random.nextInt(5));
                }
                totalEventsProcessed += 2 + random.nextInt(4);
                EventBus.getInstance().publish(new NexusEvent("CLOUD_MESH_TELEMETRY", services, "CloudMesh"));
            }
        }, 2000, 2000);
    }

    public static CloudMeshService getInstance() {
        return instance;
    }

    public void publishKafka(String topic, String key, String payload) {
        long offset = offsetCounter.incrementAndGet();
        int partition = Math.abs(key.hashCode()) % 4;
        KafkaMessage msg = new KafkaMessage(offset, topic, partition, key, payload);
        messageStream.add(0, msg);
        totalEventsProcessed++;

        // Keep last 150 messages in memory buffer
        if (messageStream.size() > 150) {
            messageStream.remove(messageStream.size() - 1);
        }

        EventBus.getInstance().publish(new NexusEvent("KAFKA_MESSAGE_PUBLISHED", msg, "CloudMesh"));
    }

    public void injectSpikeTraffic(int count) {
        new Thread(() -> {
            String[] topics = {"nexus.orders.placed", "nexus.tickets.reserved", "nexus.seats.locked", "nexus.ledger.tx", "nexus.audit.security"};
            for (int i = 0; i < count; i++) {
                String top = topics[random.nextInt(topics.length)];
                String key = "KEY-" + (100 + random.nextInt(900));
                String payload = "{\"syntheticBurst\":true,\"seq\":" + i + ",\"batchId\":\"BURST-" + System.currentTimeMillis() + "\"}";
                publishKafka(top, key, payload);
                try {
                    Thread.sleep(random.nextInt(6) + 2);
                } catch (InterruptedException ignored) {}
            }
        }).start();
    }

    public List<CloudServiceInfo> getServices() { return services; }
    public List<KafkaMessage> getMessageStream() { return messageStream; }
    public long getTotalEventsProcessed() { return totalEventsProcessed; }

    @Override
    public void onEvent(NexusEvent event) {
        String type = event.getType();
        Object payload = event.getPayload();

        if ("TICKET_BOOKED".equals(type) && payload instanceof nexus.media.CinemaBooking b) {
            publishKafka("nexus.tickets.reserved", b.getId(),
                    String.format("{\"movie\":\"%s\",\"seats\":\"%s\",\"total\":%.2f,\"pay\":\"%s\"}",
                            b.getMovieTitle(), b.getSeatsFormatted(), b.getFinalTotal(), b.getPaymentMethod()));
        } else if ("PRODUCT_PURCHASED".equals(type)) {
            publishKafka("nexus.orders.placed", "AMZ-" + System.currentTimeMillis() % 100000,
                    String.format("{\"charged\":%s,\"currency\":\"USD\",\"gateway\":\"AmazonIndia\"}", payload));
        } else if ("USER_SWITCHED".equals(type) && payload instanceof nexus.auth.UserProfile u) {
            publishKafka("nexus.user.switched", u.getId(),
                    String.format("{\"name\":\"%s\",\"role\":\"%s\",\"loc\":\"%s\"}", u.getName(), u.getRole(), u.getDeliveryAddress()));
        } else if ("TRANSACTION_ADDED".equals(type) && payload instanceof nexus.finance.Transaction t) {
            publishKafka("nexus.ledger.tx", t.getId(),
                    String.format("{\"desc\":\"%s\",\"amount\":%.2f,\"cat\":\"%s\"}", t.getDescription(), t.getAmount(), t.getCategory()));
        }
    }
}